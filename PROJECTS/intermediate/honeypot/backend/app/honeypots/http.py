import asyncio
import logging
from aiohttp import web

from ..config import settings
from ..core.broadcaster import broadcast
from ..core.geoip import lookup_ip
from ..core.patterns import score_http_request
from ..database import async_session
from ..models import HoneypotEvent, ServiceType

logger = logging.getLogger(__name__)

_LOGIN_PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>System Administration Panel</title>
<style>
  body {{ background: #1a1a2e; color: #eee; font-family: Arial, sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }}
  .box {{ background:#16213e; padding:40px; border-radius:8px; width:320px; box-shadow:0 4px 20px rgba(0,0,0,.5); }}
  h2 {{ text-align:center; margin-bottom:24px; color:#e94560; }}
  input {{ width:100%; padding:10px; margin:8px 0; background:#0f3460; border:1px solid #e94560; color:#eee; border-radius:4px; box-sizing:border-box; }}
  button {{ width:100%; padding:10px; background:#e94560; border:none; color:#fff; border-radius:4px; cursor:pointer; margin-top:12px; font-size:15px; }}
  .error {{ color:#e94560; font-size:13px; text-align:center; margin-top:8px; }}
</style>
</head>
<body>
<div class="box">
  <h2>Admin Panel</h2>
  <form method="POST" action="/login">
    <input type="text" name="username" placeholder="Username" autocomplete="off">
    <input type="password" name="password" placeholder="Password">
    <button type="submit">Login</button>
  </form>
  {error}
</div>
</body>
</html>
"""

_PATHS_LURES = {
    "/wp-admin", "/wp-login.php", "/admin", "/administrator",
    "/phpmyadmin", "/pma", "/.env", "/config.php",
    "/admin/login", "/panel", "/cpanel", "/webmail",
    "/.git/config", "/backup.zip", "/db.sql",
}


async def _save_event(ip: str, port: int, path: str, ua: str, body: str,
                      username: str = "", password: str = "") -> None:
    geo = await lookup_ip(ip)
    score, tags = score_http_request(path, body, ua)
    data = {
        "source_ip": ip,
        "source_port": port,
        "username": username or None,
        "password": password or None,
        "path": path,
        "user_agent": ua[:255] if ua else None,
        "country": geo.get("country"),
        "city": geo.get("city"),
        "threat_score": score,
        "raw_data": f"tags:{','.join(tags)}",
    }
    async with async_session() as db:
        db.add(HoneypotEvent(service=ServiceType.HTTP, **data))
        await db.commit()
    await broadcast({"service": "http", **data})


async def _handle_get(req: web.Request) -> web.Response:
    ip = req.remote or "0.0.0.0"
    port = req.transport.get_extra_info("peername", (ip, 0))[1] if req.transport else 0
    path = req.path
    ua = req.headers.get("User-Agent", "")

    asyncio.create_task(_save_event(ip, port, path, ua, ""))

    if path in _PATHS_LURES or any(path.startswith(p) for p in _PATHS_LURES):
        return web.Response(
            content_type="text/html",
            text=_LOGIN_PAGE.format(error=""),
        )

    return web.Response(content_type="text/html", text=_LOGIN_PAGE.format(error=""))


async def _handle_post(req: web.Request) -> web.Response:
    ip = req.remote or "0.0.0.0"
    port = req.transport.get_extra_info("peername", (ip, 0))[1] if req.transport else 0
    path = req.path
    ua = req.headers.get("User-Agent", "")

    try:
        data = await req.post()
        username = str(data.get("username", ""))
        password = str(data.get("password", ""))
        body = f"username={username}&password={password}"
    except Exception:
        body, username, password = "", "", ""

    asyncio.create_task(_save_event(ip, port, path, ua, body, username, password))

    return web.Response(
        content_type="text/html",
        text=_LOGIN_PAGE.format(error='<p class="error">Invalid credentials.</p>'),
    )


async def start_http_honeypot() -> None:
    app = web.Application()
    app.router.add_route("GET", "/{path_info:.*}", _handle_get)
    app.router.add_route("POST", "/{path_info:.*}", _handle_post)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, settings.http_honeypot_host, settings.http_honeypot_port)
    try:
        await site.start()
        logger.info("HTTP honeypot on port %d", settings.http_honeypot_port)
        await asyncio.Event().wait()
    except Exception as exc:
        logger.error("HTTP honeypot failed to start: %s", exc)
    finally:
        await runner.cleanup()
