from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud
from ..schemas import SummaryItem, ReadingOut
from typing import List

router = APIRouter(prefix="/api/v1", tags=["query"])

@router.get("/summary", response_model=list[SummaryItem])
def summary(db: Session = Depends(get_db)):
    return crud.latest_per_terrarium(db)

@router.get("/readings", response_model=list[ReadingOut])
def readings(terrarium: str = Query(..., description="Terrarium slug"),
             hours: int = Query(24, ge=1, le=24*30),
             db: Session = Depends(get_db)):
    rows = crud.readings_window(db, terrarium_slug=terrarium, hours=hours)
    out: list[ReadingOut] = []
    for r in rows:
        out.append(ReadingOut(
            terrarium_slug=r.terrarium.slug if r.terrarium else terrarium,
            sensor_type=r.sensor_type.value,
            value=r.value,
            unit=r.unit,
            ts=r.ts,
            entity_id=r.entity_id
        ))
    return out
