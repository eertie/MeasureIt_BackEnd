import json

from sqlalchemy import (
    ForeignKey,
    func,
    Column,
    DateTime,
    Date,
    Integer,
    String,
    Float
)
from sqlalchemy.dialects.postgresql import MONEY, JSON
from sqlalchemy.sql import text
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import synonym
from sqlalchemy.orm import relationship
from api.core.config import AppConfig
from api.core.utils import jsonEncoder
from api.models.modalBase import Base
from typing import Optional
from pydantic import BaseModel, Field, FutureDatetime, AwareDatetime, validator, JsonValue


class MeasurementDB(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(
        DateTime(timezone=AppConfig.db_useTimeZone),  server_default=func.now(), index=True
    )
    # source_id = Column(Integer, ForeignKey('sources.id'), primary_key=True, index=True, nullable=False)
    signal_id = Column(
        Integer, ForeignKey("signals.id"), index=True, nullable=False
    )
    # unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
    displayName = Column(String, nullable=True)
    valueInteger = Column(Integer, nullable=True)
    valueString = Column(String, nullable=True)
    valueFloat = Column(Float, nullable=True)
    valueJson = Column(JSON, nullable=True)
    onBeforeInsertActionId = Column(
        Integer, ForeignKey("actions.id"), nullable=True)
    onAfterInsertActionId = Column(
        Integer, ForeignKey("actions.id"), nullable=True)
    # onDeleteActionId = Column(Integer, ForeignKey('actions.id'), nullable=True)
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now()
    )
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now()
    )
    # source = relationship("Source")
    signal = relationship("SignalDB")
    # Measurement = relationship("MeasurementDB")
    # remark = relationship("Remark")
    # unit = relationship("Unit")

    def __repr__(self):
        return f"<Measurement({self.datetime} {self.displayName}>"

    @hybrid_property
    def asJson(cls):
        return json.dumps(cls.__dict__, default=jsonEncoder)

    @validator("valueJson", pre=True)
    def decode_json(cls, v):
        if not isinstance(v, str):
            try:
                return json.dumps(v)
            except BaseException as err:
                raise ValueError(
                    f"Could not parse value into valid JSON: {err}")
        return v


class Measurement(BaseModel):
    id: int
    signal_id: int
    datetime: Optional[AwareDatetime] = func.now()
    displayName: Optional[str] = None
    valueInteger: Optional[int] = None
    valueString: Optional[str] = None
    valueFloat: Optional[float] = None
    valueJson: Optional[JsonValue] = None

    class Config:
        from_attributes = True


class MeasurementCreate(BaseModel):
    signal_id: int
    datetime: Optional[AwareDatetime] = func.now()
    displayName: Optional[str] = None
    valueInteger: Optional[int] = None
    valueString: Optional[str] = None
    valueFloat: Optional[float] = None
    valueJson: Optional[JsonValue] = None

    class Config:
        from_attributes = True


class MeasurementUpdate(MeasurementCreate):
    signal_id: int
    datetime: Optional[AwareDatetime] = func.now()
    displayName: str
    valueInteger: Optional[int] = None
    valueString: Optional[str] = None
    valueFloat: Optional[float] = None
    valueJson: Optional[JsonValue] = None

    class Config:
        from_attributes = True
