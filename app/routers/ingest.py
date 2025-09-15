# app/routers/ingest.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..schemas import IngestPayload, ReadingOut
from ..database import get_db
from ..deps import verify_api_key          
from ..models import Reading, Terrarium,SensorType     
import re
from  app import crud
from app.events import event_bus
router = APIRouter(prefix="/api/v1", tags=["ingest"])

_slug_re = re.compile(r"[^a-z0-9\-]+")

def _normalize_slug(s: str) -> str:
    s = s.strip().lower().replace(" ", "-")
    return _slug_re.sub("-", s).strip("-") or "default"

@router.post("/ingest", status_code=202, response_model=ReadingOut)
async def ingest(payload: IngestPayload, db: Session = Depends(get_db)):
    slug = _normalize_slug(payload.terrarium_slug)
    terr = crud.get_or_create_terrarium(db, slug)

    sensor_type = SensorType(payload.sensor_type)  
    reading = crud.create_reading(
        db=db,
        terrarium=terr,
        sensor_type=sensor_type,
        value=payload.value,
        unit=payload.unit,
        entity_id=payload.entity_id,
        ts=payload.ts,
    )

    if getattr(payload, "role", None) and payload.entity_id:
        from ..models import SensorRoleName
        crud.set_role(db, terrarium_slug=terr.slug,
                      role=SensorRoleName(payload.role), entity_id=payload.entity_id)

    await event_bus.publish({"terrarium": terr.slug, "sensor_type": sensor_type.value})

    return ReadingOut(
        terrarium_slug=terr.slug,
        sensor_type=sensor_type.value,
        value=reading.value,
        unit=reading.unit,
        entity_id=reading.entity_id,
        ts=reading.ts,
    )
