from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal, Optional

RoleName = Literal["basking_temp", "env_temp", "humidity"]

class IngestPayload(BaseModel):
    terrarium_slug: str
    sensor_type: Literal["temperature", "humidity"]
    value: float | None  
    unit: str
    entity_id: str | None = None
    ts: datetime
    role: RoleName | None = None
    available: bool | None = None


class RoleMapRequest(BaseModel):
    terrarium_slug: str
    role: RoleName
    entity_id: str

class TerrariumOut(BaseModel):
    id: int
    slug: str
    name: str | None

    model_config = ConfigDict(from_attributes=True)

class ReadingOut(BaseModel):
    terrarium_slug: str
    sensor_type: str
    value: float
    unit: str
    ts: datetime
    entity_id: str | None = None

class SummaryItem(BaseModel):
    terrarium_slug: str
    temperature: float | None = None
    temperature_unit: str | None = None
    humidity: float | None = None
    humidity_unit: str | None = None
    ts_temperature: datetime | None = None
    ts_humidity: datetime | None = None

class RoleSummaryItem(BaseModel):
    terrarium_slug: str
    basking_temp: float | None = None
    basking_temp_unit: str | None = None
    basking_temp_ts: datetime | None = None
    env_temp: float | None = None
    env_temp_unit: str | None = None
    env_temp_ts: datetime | None = None
    humidity: float | None = None
    humidity_unit: str | None = None
    humidity_ts: datetime | None = None