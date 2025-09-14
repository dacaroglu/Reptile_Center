# app/routers/sse.py
from __future__ import annotations
from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse
import asyncio

from ..events import event_bus
from ..database import SessionLocal
from .. import crud
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["sse"])
templates = Jinja2Templates(directory="app/templates")

def _sse(event: str, data: str):
    yield f"event: {event}\n"
    for line in data.splitlines():
        yield f"data: {line}\n"
    yield "\n"

@router.get("/sse/summary")
async def sse_summary(request: Request):
    q = await event_bus.subscribe()

    async def gen():
        try:
            # initial render
            db = SessionLocal()
            items = crud.latest_per_terrarium(db)
            db.close()
            html = templates.get_template("components/summary_table.html").render(
                {"request": request, "items": items}
            )
            for chunk in _sse("summary", html):
                yield chunk

            # stream updates
            while True:
                if await request.is_disconnected():
                    break
                try:
                    await asyncio.wait_for(q.get(), timeout=25)
                except asyncio.TimeoutError:
                    # heartbeat to keep proxies happy
                    yield ": keep-alive\n\n"
                    continue

                db = SessionLocal()
                items = crud.latest_per_terrarium(db)
                db.close()
                html = templates.get_template("components/summary_table.html").render(
                    {"request": request, "items": items}
                )
                for chunk in _sse("summary", html):
                    yield chunk
        finally:
            await event_bus.unsubscribe(q)

    return StreamingResponse(gen(), media_type="text/event-stream")
