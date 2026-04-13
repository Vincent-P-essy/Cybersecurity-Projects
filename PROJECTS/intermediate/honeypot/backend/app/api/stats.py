from fastapi import APIRouter, Depends
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import HoneypotEvent, ServiceType

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count()).select_from(HoneypotEvent))).scalar_one()
    unique_ips = (await db.execute(select(func.count(func.distinct(HoneypotEvent.source_ip))))).scalar_one()
    max_score = (await db.execute(select(func.max(HoneypotEvent.threat_score)))).scalar_one() or 0

    by_service_rows = (
        await db.execute(
            select(HoneypotEvent.service, func.count().label("cnt"))
            .group_by(HoneypotEvent.service)
        )
    ).all()
    by_service = {row.service.value: row.cnt for row in by_service_rows}

    top_ips_rows = (
        await db.execute(
            select(HoneypotEvent.source_ip, func.count().label("cnt"))
            .group_by(HoneypotEvent.source_ip)
            .order_by(func.count().desc())
            .limit(10)
        )
    ).all()
    top_ips = [{"ip": r.source_ip, "count": r.cnt} for r in top_ips_rows]

    top_usernames_rows = (
        await db.execute(
            select(HoneypotEvent.username, func.count().label("cnt"))
            .where(HoneypotEvent.username.isnot(None))
            .where(HoneypotEvent.username != "")
            .group_by(HoneypotEvent.username)
            .order_by(func.count().desc())
            .limit(10)
        )
    ).all()
    top_usernames = [{"username": r.username, "count": r.cnt} for r in top_usernames_rows]

    top_passwords_rows = (
        await db.execute(
            select(HoneypotEvent.password, func.count().label("cnt"))
            .where(HoneypotEvent.password.isnot(None))
            .where(HoneypotEvent.password != "")
            .group_by(HoneypotEvent.password)
            .order_by(func.count().desc())
            .limit(10)
        )
    ).all()
    top_passwords = [{"password": r.password, "count": r.cnt} for r in top_passwords_rows]

    top_countries_rows = (
        await db.execute(
            select(HoneypotEvent.country, func.count().label("cnt"))
            .where(HoneypotEvent.country.isnot(None))
            .group_by(HoneypotEvent.country)
            .order_by(func.count().desc())
            .limit(10)
        )
    ).all()
    top_countries = [{"country": r.country, "count": r.cnt} for r in top_countries_rows]

    return {
        "total_events": total,
        "unique_ips": unique_ips,
        "max_threat_score": max_score,
        "by_service": by_service,
        "top_ips": top_ips,
        "top_usernames": top_usernames,
        "top_passwords": top_passwords,
        "top_countries": top_countries,
    }
