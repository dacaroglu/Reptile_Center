# app/routers/ingest.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..schemas import IngestPayload, ReadingOut
from ..database import get_db
from ..deps import verify_api_key          # ✅ use this name
from ..models import Reading, Terrarium     # (drop unused imports)

router = APIRouter(prefix="/api/v1", tags=["ingest"])

# ✅ with a prefix above, the route here must be just "/ingest"
@router.post("/ingest", response_model=ReadingOut, status_code=202,
             dependencies=[Depends(verify_api_key)])
async def ingest(payload: IngestPayload, request: Request, db: Session = Depends(get_db)):
    terr = db.query(Terrarium).filter(Terrarium.slug == payload.terrarium_slug).one_or_none()
    if not terr:
        raise HTTPException(status_code=404, detail="Terrarium not found")

    available = payload.available if payload.available is not None else (payload.value is not None)

    row = Reading(
        terrarium_id=terr.id,
        sensor_type=payload.sensor_type,
        value=payload.value,           # may be None (DB must allow NULL)
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
