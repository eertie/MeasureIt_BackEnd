from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, func, JSON, Date, Boolean, Text, Column, DateTime, Date, Integer, String, Numeric
# from sqlalchemy.ext.declarative import declarative_base
from api.core.config import AppConfig
from api.models.modalBase import Base
from pydantic import BaseModel
from typing import Optional


class UnitDB(Base):
    __tablename__ = "units"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), index=True, unique=True)
    displayName = Column(String(20))
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())


class Unit(BaseModel):
    id: int
    name: str
    displayName: Optional[str]

    class Config:
        from_attributes = True


class UnitCreate(BaseModel):
    name: str
    displayName:  Optional[str]

    class Config:
        from_attributes = True


class UnitUpdate(UnitCreate):
    name:  Optional[str]
