from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal

class IngestPayload(BaseModel):
    terrarium_slug: str = Field(min_length=1, max_length=50)
    sensor_type: Literal["temperature", "humidity"]
    value: float
    unit: str = Field(min_length=1, max_length=16)
    entity_id: str | None = Field(default=None, max_length=128)
    ts: datetime  # ISO8601 from HA; assumed UTC or local (we'll coerce to UTC in server)

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
