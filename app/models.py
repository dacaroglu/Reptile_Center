from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum, func, Index
from datetime import datetime, timezone
import enum
from .database import Base

class SensorType(str, enum.Enum):
    temperature = "temperature"
    humidity = "humidity"

class Terrarium(Base):
    __tablename__ = "terrariums"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    readings: Mapped[list["Reading"]] = relationship(back_populates="terrarium", cascade="all, delete-orphan")

class Reading(Base):
    __tablename__ = "readings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    terrarium_id: Mapped[int] = mapped_column(ForeignKey("terrariums.id", ondelete="CASCADE"), index=True)
    sensor_type: Mapped[SensorType] = mapped_column(Enum(SensorType), index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(16))
    entity_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    terrarium: Mapped["Terrarium"] = relationship(back_populates="readings")

Index("ix_readings_terrarium_type_ts", Reading.terrarium_id, Reading.sensor_type, Reading.ts.desc())
