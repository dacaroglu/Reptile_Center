from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta, timezone
from .models import Terrarium, Reading, SensorType, SensorRole, SensorRoleName

def get_or_create_terrarium(db, slug: str) -> Terrarium:
    """Return existing terrarium by slug or create it on first use."""
    terr = db.execute(select(Terrarium).where(Terrarium.slug == slug)).scalar_one_or_none()
    if terr:
        return terr

    terr = Terrarium(slug=slug)            # if your model has 'name', you can also set name=slug
    db.add(terr)
    try:
        db.commit()
    except IntegrityError:
        # created by a concurrent request; fetch it
        db.rollback()
        terr = db.execute(select(Terrarium).where(Terrarium.slug == slug)).scalar_one()
    db.refresh(terr)
    return terr

def create_reading(db: Session, terrarium: Terrarium, sensor_type: SensorType, value: float, unit: str, entity_id: str | None, ts: datetime) -> Reading:
    r = Reading(
        terrarium=terrarium,
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
def list_seen_sensors(db: Session, terrarium_slug: str):
    """Distinct entity_ids seen for this terrarium."""
    t = db.scalar(select(Terrarium).where(Terrarium.slug == terrarium_slug))
    if not t:
        return []
    rows = db.execute(
        select(Reading.entity_id, Reading.sensor_type)
        .where(Reading.terrarium_id == t.id, Reading.entity_id.is_not(None))
        .group_by(Reading.entity_id, Reading.sensor_type)
    ).all()
    return [{"entity_id": e, "sensor_type": s.value if hasattr(s, "value") else s} for e, s in rows if e]

def set_role(db: Session, terrarium_slug: str, role: SensorRoleName, entity_id: str):
    t = get_or_create_terrarium(db, terrarium_slug)
    # upsert
    existing = db.scalar(select(SensorRole).where(SensorRole.terrarium_id == t.id, SensorRole.role == role))
    if existing:
        existing.entity_id = entity_id
    else:
        db.add(SensorRole(terrarium_id=t.id, role=role, entity_id=entity_id))
    db.commit()

def get_role_map(db: Session, terrarium_slug: str) -> dict[str, str]:
    t = db.scalar(select(Terrarium).where(Terrarium.slug == terrarium_slug))
    if not t:
        return {}
    rows = db.execute(select(SensorRole).where(SensorRole.terrarium_id == t.id)).scalars().all()
    return {r.role.value: r.entity_id for r in rows}

def role_summary(db: Session):
    """
    For each terrarium, return latest reading for each canonical role (if mapped).
    """
    # load all terrariums
    terrs = db.execute(select(Terrarium)).scalars().all()
    out = []
    for t in terrs:
        # role->entity map
        roles = db.execute(select(SensorRole).where(SensorRole.terrarium_id == t.id)).scalars().all()
        role_map = {r.role: r.entity_id for r in roles}

        # helper to fetch latest by entity_id
        def latest_by_entity(eid: str) -> Reading | None:
            return db.execute(
                select(Reading).where(Reading.terrarium_id == t.id, Reading.entity_id == eid)
                .order_by(Reading.ts.desc())
                .limit(1)
            ).scalar_one_or_none()

        item = {
            "terrarium_slug": t.slug,
            "basking_temp": None, "basking_temp_unit": None, "basking_temp_ts": None,
            "env_temp": None, "env_temp_unit": None, "env_temp_ts": None,
            "humidity": None, "humidity_unit": None, "humidity_ts": None,
        }

        if SensorRoleName.basking_temp in role_map:
            r = latest_by_entity(role_map[SensorRoleName.basking_temp])
            if r:
                item["basking_temp"] = r.value
                item["basking_temp_unit"] = r.unit
                item["basking_temp_ts"] = r.ts

        if SensorRoleName.env_temp in role_map:
            r = latest_by_entity(role_map[SensorRoleName.env_temp])
            if r:
                item["env_temp"] = r.value
                item["env_temp_unit"] = r.unit
                item["env_temp_ts"] = r.ts

        if SensorRoleName.humidity in role_map:
            r = latest_by_entity(role_map[SensorRoleName.humidity])
            if r:
                item["humidity"] = r.value
                item["humidity_unit"] = r.unit
                item["humidity_ts"] = r.ts

        out.append(item)
    return out