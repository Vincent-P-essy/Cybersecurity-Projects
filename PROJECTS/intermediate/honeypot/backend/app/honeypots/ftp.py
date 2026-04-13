import asyncio
import logging

from ..config import settings
from ..core.broadcaster import broadcast
from ..core.geoip import lookup_ip
from ..database import async_session
from ..models import HoneypotEvent, ServiceType

logger = logging.getLogger(__name__)

_FAKE_LISTING = """\
-rw-r--r-- 1 ftp ftp    4096 Nov 14 08:00 backup.tar.gz
-rw-r--r-- 1 ftp ftp   12345 Nov 12 15:30 database_dump.sql
drwxr-xr-x 2 ftp ftp    4096 Nov 10 09:00 uploads
-rw------- 1 ftp ftp     256 Nov 08 11:22 .htpasswd
"""


async def _save_event(ip: str, port: int, username: str, password: str, command: str | None = None) -> None:
    geo = await lookup_ip(ip)
    data = {
        "source_ip": ip,
        "source_port": port,
        "username": username,
        "password": password,
        "command": command,
        "country": geo.get("country"),
        "city": geo.get("city"),
        "threat_score": 20,
    }
    async with async_session() as db:
        db.add(HoneypotEvent(service=ServiceType.FTP, **data))
        await db.commit()
    await broadcast({"service": "ftp", **data})


class _FTPSession(asyncio.Protocol):
    def __init__(self) -> None:
        self._transport: asyncio.Transport | None = None
        self._ip = "0.0.0.0"
        self._port = 0
        self._username = ""
        self._authenticated = False

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self._transport = transport  # type: ignore[assignment]
        peer = transport.get_extra_info("peername", ("0.0.0.0", 0))
        self._ip, self._port = peer
        logger.info("FTP connect from %s:%d", self._ip, self._port)
        self._send("220 FTP Server ready.")

    def _send(self, msg: str) -> None:
        if self._transport:
            self._transport.write((msg + "\r\n").encode())

    def data_received(self, data: bytes) -> None:
        try:
            line = data.decode(errors="replace").strip()
        except Exception:
            return

        parts = line.split(None, 1)
        cmd = parts[0].upper() if parts else ""
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "USER":
            self._username = arg
            self._send(f"331 Password required for {arg}.")
        elif cmd == "PASS":
            logger.info("FTP auth %s:%d  %s / %s", self._ip, self._port, self._username, arg)
            asyncio.create_task(_save_event(self._ip, self._port, self._username, arg))
            self._authenticated = True
            self._send("230 Login successful.")
        elif cmd == "SYST":
            self._send("215 UNIX Type: L8")
        elif cmd == "FEAT":
            self._send("211-Features:\r\n PASV\r\n UTF8\r\n211 End")
        elif cmd == "PWD":
            self._send('257 "/" is the current directory')
        elif cmd in ("LIST", "NLST"):
            self._send("150 Here comes the directory listing.")
            self._send(_FAKE_LISTING)
            self._send("226 Directory send OK.")
            asyncio.create_task(_save_event(self._ip, self._port, self._username, "", cmd))
        elif cmd in ("CWD", "CDUP"):
            self._send("250 Directory successfully changed.")
        elif cmd == "RETR":
            self._send("550 Failed to open file.")
        elif cmd in ("STOR", "STOU"):
            self._send("550 Permission denied.")
        elif cmd == "PASV":
            self._send("227 Entering Passive Mode (0,0,0,0,0,0).")
        elif cmd == "TYPE":
            self._send(f"200 Switching to {'Binary' if arg == 'I' else 'ASCII'} mode.")
        elif cmd in ("QUIT", "BYE"):
            self._send("221 Goodbye.")
            if self._transport:
                self._transport.close()
        else:
            self._send(f"502 Command not implemented: {cmd}")

    def connection_lost(self, exc: Exception | None) -> None:
        logger.debug("FTP disconnect from %s:%d", self._ip, self._port)


async def start_ftp_honeypot() -> None:
    loop = asyncio.get_event_loop()
    try:
        server = await loop.create_server(
            _FTPSession,
            settings.ftp_host,
            settings.ftp_port,
        )
        logger.info("FTP honeypot on port %d", settings.ftp_port)
        async with server:
            await server.serve_forever()
    except Exception as exc:
        logger.error("FTP honeypot failed to start: %s", exc)
