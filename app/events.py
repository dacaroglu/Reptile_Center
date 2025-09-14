# app/events.py
import asyncio
from typing import Any, Set

class EventBus:
    def __init__(self) -> None:
        self._subs: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        async with self._lock:
            self._subs.add(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue) -> None:
        async with self._lock:
            self._subs.discard(q)

    async def publish(self, item: Any) -> None:
        async with self._lock:
            subs = list(self._subs)
        for q in subs:
            try:
                q.put_nowait(item)
            except asyncio.QueueFull:
                pass  # drop if a client is slow

event_bus = EventBus()
