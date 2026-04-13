import asyncio
from typing import Set

_subscribers: Set[asyncio.Queue] = set()


def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    _subscribers.add(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    _subscribers.discard(q)


async def broadcast(data: dict) -> None:
    dead = set()
    for q in _subscribers.copy():
        try:
            q.put_nowait(data)
        except asyncio.QueueFull:
            dead.add(q)
    _subscribers.difference_update(dead)
