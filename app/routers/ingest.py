from __future__ import annotations
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from datetime import timezone
from ..schemas import IngestPayload, ReadingOut
from ..database import get_db
from ..deps import verify_api_key
from .. import crud, models
from ..events import event_bus

router = APIRouter(prefix="/api/v1", tags=["ingest"])

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED, response_model=ReadingOut, dependencies=[Depends(verify_api_key)])
async def ingest(payload: IngestPayload, db: Session = Depends(get_db)):
    # normalize timestamp to UTC
    ts = payload.ts
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    else:
        ts = ts.astimezone(timezone.utc)

    terr = crud.get_or_create_terrarium(db, payload.terrarium_slug)
    sensor_type = models.SensorType(payload.sensor_type)
    reading = crud.create_reading(
        db,
        terrarium=terr,
        sensor_type=sensor_type,
        value=payload.value,
        unit=payload.unit,
        entity_id=payload.entity_id,
        ts=ts,
    )
    await event_bus.publish({"terrarium": terr.slug, "sensor_type": sensor_type.value})

    return ReadingOut(
        terrarium_slug=terr.slug,
        sensor_type=sensor_type.value,
        value=reading.value,
        unit=reading.unit,
        ts=reading.ts,
        entity_id=reading.entity_id,
    )