import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

_cache: dict[str, dict] = {}
_PRIVATE_RANGES = ("10.", "172.", "192.168.", "127.", "::1", "0.0.0.0")


def _is_private(ip: str) -> bool:
    return any(ip.startswith(prefix) for prefix in _PRIVATE_RANGES)


async def lookup_ip(ip: str) -> dict:
    if ip in _cache:
        return _cache[ip]

    if _is_private(ip):
        result = {"country": "Private", "city": "LAN", "countryCode": "XX"}
        _cache[ip] = result
        return result

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city")
            data = resp.json()
            if data.get("status") == "success":
                result = {
                    "country": data.get("country", "Unknown"),
                    "countryCode": data.get("countryCode", "XX"),
                    "city": data.get("city", "Unknown"),
                }
                _cache[ip] = result
                return result
    except Exception as e:
        logger.debug(f"GeoIP lookup failed for {ip}: {e}")

    fallback = {"country": "Unknown", "city": "Unknown", "countryCode": "XX"}
    _cache[ip] = fallback
    return fallback
