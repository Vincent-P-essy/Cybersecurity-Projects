import asyncio
import asyncssh
import logging
import os
from datetime import datetime

from ..config import settings
from ..core.broadcaster import broadcast
from ..core.geoip import lookup_ip
from ..core.patterns import score_ssh_command
from ..database import async_session
from ..models import HoneypotEvent, ServiceType

logger = logging.getLogger(__name__)

_MOTD = """\
Linux prod-server 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023 x86_64

Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-91-generic x86_64)

Last login: {dt} from 192.168.1.1
"""

_RESPONSES: dict[str, str] = {
    "id": "uid=0(root) gid=0(root) groups=0(root)",
    "whoami": "root",
    "uname -a": "Linux prod-server 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023 x86_64 GNU/Linux",
    "hostname": "prod-server",
    "pwd": "/root",
    "ls": "backup  logs  scripts  .bash_history  .ssh",
    "ls -la": "total 32\ndrwx------ 4 root root 4096 Nov 14 10:22 .\ndrwxr-xr-x 19 root root 4096 Nov 12 08:01 ..\n-rw------- 1 root root  512 Nov 14 10:22 .bash_history\ndrwxr-xr-x 2 root root 4096 Nov 12 08:05 backup\ndrwxr-xr-x 2 root root 4096 Nov 12 08:05 logs\ndrwxr-xr-x 2 root root 4096 Nov 12 08:05 scripts\ndrwx------ 2 root root 4096 Nov 12 08:01 .ssh",
    "cat /etc/passwd": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin",
    "cat /etc/shadow": "cat: /etc/shadow: Permission denied",
    "ifconfig": "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n        inet 10.0.0.5  netmask 255.255.255.0",
    "ip a": "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536\n2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500\n    inet 10.0.0.5/24 brd 10.0.0.255 scope global eth0",
    "ps aux": "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\nroot         1  0.0  0.0  22544  1644 ?        Ss   Nov14   0:00 /sbin/init\nroot       312  0.0  0.0  72296  6012 ?        Ss   Nov14   0:00 sshd: /usr/sbin/sshd -D",
    "netstat -an": "Active Internet connections (servers and established)\nProto Recv-Q Send-Q Local Address           Foreign Address         State\ntcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN",
    "history": "    1  apt-get update\n    2  apt-get upgrade -y\n    3  ls /home\n    4  cat /etc/passwd\n    5  exit",
    "env": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\nHOME=/root\nUSER=root\nSHELL=/bin/bash",
    "w": " 10:33:01 up 2 days,  2:11,  1 user,  load average: 0.00, 0.00, 0.00\nUSER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT\nroot     pts/0    10.0.0.1         10:33    0.00s  0.00s  0.00s w",
}


async def _save_event(source_ip: str, source_port: int, username: str, password: str,
                      command: str | None = None) -> None:
    geo = await lookup_ip(source_ip)
    score = 10
    if command:
        score, _ = score_ssh_command(command)

    event_data = {
        "source_ip": source_ip,
        "source_port": source_port,
        "username": username,
        "password": password if not command else None,
        "command": command,
        "country": geo.get("country"),
        "city": geo.get("city"),
        "threat_score": score,
    }

    async with async_session() as db:
        db.add(HoneypotEvent(service=ServiceType.SSH, **event_data))
        await db.commit()

    await broadcast({"service": "ssh", **event_data})


class _FakeShell(asyncssh.SSHServerSession):
    def __init__(self, username: str, ip: str, port: int) -> None:
        self._username = username
        self._ip = ip
        self._port = port
        self._buf = ""

    def shell_requested(self) -> bool:
        return True

    def connection_made(self, chan: asyncssh.SSHServerChannel) -> None:
        self._chan = chan
        motd = _MOTD.format(dt=datetime.now().strftime("%a %b %d %H:%M:%S %Y"))
        chan.write(motd + "\nroot@prod-server:~# ")

    def data_received(self, data: str, datatype: asyncssh.DataType) -> None:
        self._buf += data
        if "\n" not in self._buf and "\r" not in self._buf:
            return

        cmd = self._buf.strip()
        self._buf = ""

        if not cmd:
            self._chan.write("root@prod-server:~# ")
            return

        if cmd in ("exit", "logout", "quit"):
            self._chan.write("logout\n")
            self._chan.close()
            return

        response = _RESPONSES.get(cmd, f"bash: {cmd.split()[0]}: command not found")
        self._chan.write(response + "\nroot@prod-server:~# ")
        asyncio.create_task(_save_event(self._ip, self._port, self._username, "", cmd))

    def eof_received(self) -> None:
        self._chan.close()


class _SSHHoneypotServer(asyncssh.SSHServer):
    def __init__(self) -> None:
        self._username = "unknown"
        self._peer: tuple[str, int] = ("0.0.0.0", 0)

    def connection_made(self, conn: asyncssh.SSHServerConnection) -> None:
        self._peer = conn.get_extra_info("peername", ("0.0.0.0", 0))
        logger.info("SSH connect from %s:%d", *self._peer)

    def password_auth_supported(self) -> bool:
        return True

    async def validate_password(self, username: str, password: str) -> bool:
        ip, port = self._peer
        self._username = username
        logger.info("SSH auth %s:%d  %s / %s", ip, port, username, password)
        asyncio.create_task(_save_event(ip, port, username, password))
        return True

    def session_requested(self) -> asyncssh.SSHServerSession:
        return _FakeShell(self._username, *self._peer)


async def _ensure_host_key() -> None:
    path = settings.ssh_host_key_path
    if not os.path.exists(path):
        key = asyncssh.generate_private_key("ssh-rsa")
        key.write_private_key(path)
        os.chmod(path, 0o600)


async def start_ssh_honeypot() -> None:
    await _ensure_host_key()
    try:
        await asyncssh.create_server(
            _SSHHoneypotServer,
            settings.ssh_host,
            settings.ssh_port,
            server_host_keys=[settings.ssh_host_key_path],
        )
        logger.info("SSH honeypot on port %d", settings.ssh_port)
    except Exception as exc:
        logger.error("SSH honeypot failed to start: %s", exc)
