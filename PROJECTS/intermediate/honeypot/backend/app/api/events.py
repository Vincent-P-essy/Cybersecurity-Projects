import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.broadcaster import subscribe, unsubscribe
from ..database import get_db
from ..models import HoneypotEvent, ServiceType

router = APIRouter(prefix="/api/events", tags=["events"])


def _serialize(ev: HoneypotEvent) -> dict:
    return {
        "id": ev.id,
        "service": ev.service.value if ev.service else None,
        "source_ip": ev.source_ip,
        "source_port": ev.source_port,
        "username": ev.username,
        "password": ev.password,
        "command": ev.command,
        "path": ev.path,
        "user_agent": ev.user_agent,
        "country": ev.country,
        "city": ev.city,
        "threat_score": ev.threat_score,
        "created_at": ev.created_at.isoformat() if ev.created_at else None,
    }


@router.get("")
async def list_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    service: ServiceType | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(HoneypotEvent).order_by(HoneypotEvent.created_at.desc())
    if service:
        q = q.where(HoneypotEvent.service == service)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    q = q.offset((page - 1) * limit).limit(limit)
    rows = (await db.execute(q)).scalars().all()

    return {"total": total, "page": page, "limit": limit, "events": [_serialize(r) for r in rows]}


@router.get("/stream")
async def stream_events():
    q = subscribe()

    async def _generator():
        try:
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            unsubscribe(q)

    return StreamingResponse(
        _generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.delete("")
async def clear_events(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(HoneypotEvent))
    await db.commit()
    return {"deleted": True}
