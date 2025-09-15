# app/routers/sse.py
from __future__ import annotations
import asyncio
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import StreamingResponse

from ..events import event_bus
from ..database import SessionLocal
from .. import crud

router = APIRouter(tags=["sse"])
templates = Jinja2Templates(directory="app/templates")


def _sse(event: str, data: str):
    """Helper: format one SSE event from an HTML fragment."""
    yield f"event: {event}\n"
    for line in data.splitlines():
        yield f"data: {line}\n"
    yield "\n"


@router.get("/sse/summary")
async def sse_summary(request: Request):
    q = await event_bus.subscribe()

    async def gen():
        try:
            # Initial render
            with SessionLocal() as db:
                # If you added role_summary, prefer it; otherwise use latest_per_terrarium
                items = crud.role_summary(db) if hasattr(crud, "role_summary") else crud.latest_per_terrarium(db)
            html = templates.get_template("components/summary_table.html").render(
                {"request": request, "items": items}
            )
            for chunk in _sse("summary", html):
                yield chunk

            # Live loop
            while True:
                if await request.is_disconnected():
                    break

                try:
                    # heartbeat every ~25s to keep proxies happy
                    await asyncio.wait_for(q.get(), timeout=25)
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
                    continue

                with SessionLocal() as db:
                    items = crud.role_summary(db) if hasattr(crud, "role_summary") else crud.latest_per_terrarium(db)
                html = templates.get_template("components/summary_table.html").render(
                    {"request": request, "items": items}
                )
                for chunk in _sse("summary", html):
                    yield chunk
        finally:
            await event_bus.unsubscribe(q)

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # nginx: disable proxy buffering
            "Connection": "keep-alive",
        },
    )
