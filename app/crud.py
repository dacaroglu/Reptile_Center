from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta, timezone
from .models import Terrarium, Reading, SensorType

def get_or_create_terrarium(db: Session, slug: str) -> Terrarium:
    t = db.scalar(select(Terrarium).where(Terrarium.slug == slug))
    if t:
        return t
    t = Terrarium(slug=slug, name=slug.replace("-", " ").title())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

def create_reading(db: Session, terrarium: Terrarium, sensor_type: SensorType, value: float, unit: str, entity_id: str | None, ts: datetime) -> Reading:
    r = Reading(
        terrarium_id=terrarium.id,
        sensor_type=sensor_type,
        value=value,
        unit=unit,
        entity_id=entity_id,
        ts=ts,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def latest_per_terrarium(db: Session):
    # Grab latest temperature and humidity per terrarium
    # Subqueries for latest ts per (terrarium, sensor_type)
    latest_ts = (
        select(Reading.terrarium_id, Reading.sensor_type, func.max(Reading.ts).label("max_ts"))
        .group_by(Reading.terrarium_id, Reading.sensor_type)
        .subquery()
    )
    latest_rows = db.execute(
        select(Reading, Terrarium.slug)
        .join(latest_ts, (Reading.terrarium_id == latest_ts.c.terrarium_id) & (Reading.sensor_type == latest_ts.c.sensor_type) & (Reading.ts == latest_ts.c.max_ts))
        .join(Terrarium, Terrarium.id == Reading.terrarium_id)
    ).all()

    # organize
    by_slug: dict[str, dict] = {}
    for r, slug in latest_rows:
        d = by_slug.setdefault(slug, {})
        if r.sensor_type == SensorType.temperature:
            d["temperature"] = r.value
            d["temperature_unit"] = r.unit
            d["ts_temperature"] = r.ts
        elif r.sensor_type == SensorType.humidity:
            d["humidity"] = r.value
            d["humidity_unit"] = r.unit
            d["ts_humidity"] = r.ts
    # merge into list
    out = []
    for slug, vals in by_slug.items():
        out.append({
            "terrarium_slug": slug,
            **vals
        })
    return out

def readings_window(db: Session, terrarium_slug: str, hours: int = 24):
    row = db.execute(select(Terrarium).where(Terrarium.slug == terrarium_slug)).scalar_one_or_none()
    if not row:
        return []

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = db.execute(
        select(Reading).where(Reading.terrarium_id == row.id, Reading.ts >= since).order_by(Reading.ts.asc())
    ).scalars().all()

    return rows
