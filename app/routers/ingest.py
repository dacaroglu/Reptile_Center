# app/routers/ingest.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..schemas import IngestPayload, ReadingOut
from ..models import Reading, Terrarium
from ..database import get_db
# ... auth etc.

@router.post("/api/v1/ingest", response_model=ReadingOut, status_code=202, dependencies=[Depends(require_api_key)])
async def ingest(payload: IngestPayload, request: Request, db: Session = Depends(get_db)):
    terr = db.query(Terrarium).filter(Terrarium.slug == payload.terrarium_slug).one_or_none()
    if not terr:
        raise HTTPException(404, "Terrarium not found")

    # default available: True when value is present, False when it's null
    available = payload.available if payload.available is not None else (payload.value is not None)

    row = Reading(
        terrarium_id=terr.id,
        sensor_type=payload.sensor_type,
        value=payload.value,     # may be None
        unit=payload.unit,
        entity_id=payload.entity_id,
        ts=payload.ts,
        available=available,
    )
    db.add(row)
    db.commit()

    return ReadingOut(
        terrarium_slug=terr.slug,
        sensor_type=row.sensor_type,
        value=row.value,
        unit=row.unit,
        entity_id=row.entity_id,
        ts=row.ts,
        available=row.available,
    )
