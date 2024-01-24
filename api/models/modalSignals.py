from sqlalchemy import (UniqueConstraint, Column, Sequence, Integer, String, Boolean, ForeignKey,
                        func, JSON, Text, Column, DateTime, Date, Integer, String, Numeric)
from pydantic import BaseModel
from sqlalchemy.orm import relationship
from api.core.config import AppConfig
from api.models.modalBase import Base
from typing import Optional
from datetime import datetime


class SignalDB(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=True)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())

    # device = relationship('DeviceDB', backref='signals', cascade='delete')
    # unit = relationship('UnitDB', backref='signals', cascade='delete')
    device = relationship('DeviceDB')
    unit = relationship('UnitDB')

    # Define a composite unique constraint on device_id, unit_id and name
    __table_args__ = (
        UniqueConstraint('device_id', 'unit_id', 'name'),
    )


class Signal(BaseModel):
    id: int
    device_id: Optional[int] = None
    unit_id: Optional[int] = None
    name: str
    description:  Optional[str] = None

    class Config:
        from_attributes = True


class SignalCreate(BaseModel):
    device_id: Optional[int] = None
    unit_id: Optional[int] = None
    name: str
    description:  Optional[str] = None

    class Config:
        from_attributes = True


class SignalUpdate(SignalCreate):
    name: Optional[str] = None
