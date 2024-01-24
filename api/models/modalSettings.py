from pydantic import BaseModel, ValidationError
from sqlalchemy import ForeignKey, func, JSON, Date, Boolean, Text, Column, DateTime, Date, Integer, String, Numeric
from sqlalchemy.dialects.postgresql import MONEY
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from api.core.config import AppConfig
from api.models.modalBase import Base
from api.core.utils import AppResponse
from api import logger


class SettingDB(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, unique=True)
    value = Column(String)
    # valueNumeric = Column(Numeric)
    # valueInteger = Column(Integer)
    # valueBoolean = Column(Boolean)
    # valueJson = Column(JSON)
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())


class Setting(BaseModel):
    id: int
    name: str
    value: str
    # valueNumeric: Optional[float]
    # valueInteger: Optional[int]
    # valueBoolean: Optional[bool]
    # valueJson :Optional[Json]

    class Config:
        from_attributes = True


class SettingCreate(BaseModel):
    name: str
    value: str
    # valueNumeric: Optional[float]
    # valueInteger: Optional[int]
    # valueBoolean: Optional[bool]
    # valueJson :Optional[Json]

    class Config:
        from_attributes = True


class SettingUpdate(SettingCreate):
    pass
