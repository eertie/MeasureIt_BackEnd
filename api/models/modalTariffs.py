from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, func, Column, DateTime, Integer, String, Numeric
from sqlalchemy.orm import relationship
from api.core.config import AppConfig
from api.models.modalBase import Base
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, FutureDatetime, AwareDatetime
from api.core.config import AppConfig
from typing import Union


class TariffDB(Base):
    __tablename__ = "tariffs"
    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey(
        'signals.id'), index=True, nullable=False)
    startDate = Column(DateTime(timezone=AppConfig.db_useTimeZone), index=True)
    remark = Column(String(50))
    unit_cost1 = Column(Numeric(precision=10, scale=5))
    unit_cost2 = Column(Numeric(precision=10, scale=5))
    unit_cost3 = Column(Numeric(precision=10, scale=5))
    currency = Column(String(5), default=AppConfig.app_currency)
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())
    signal = relationship("SignalDB")

    __table_args__ = (
        UniqueConstraint('signal_id', 'startDate'),
    )

    def __repr__(self):
        dt = self.startDate.strftime("%Y-%m-%d, %H:%M:%S")
        return f"<Tariff({self.id}, startDate={dt}, signal={self.signal}, costs1={self.costs1}>"


class Tariff(BaseModel):
    id: int
    signal_id: int
    startDate: Union[FutureDatetime, AwareDatetime]
    remark: Optional[str] = None
    unit_cost: float
    # costs2: Optional[float] = None
    # costs3: Optional[float] = None
    currency: str = Field(default=AppConfig.app_currency)

    class Config:
        from_attributes = True


class TariffCreate(BaseModel):
    signal_id: int
    startDate: Union[FutureDatetime, AwareDatetime]
    remark: Optional[str] = None
    unit_cost: float
    # costs2: Optional[float] = None
    # costs3: Optional[float] = None
    currency: str = Field(default=AppConfig.app_currency)

    class Config:
        from_attributes = True


class TariffUpdate(TariffCreate):
    startDate: Optional[Union[FutureDatetime, AwareDatetime]] = None
    remark: Optional[str] = None
    unit_cost: Optional[float] = None
    # costs2: Optional[float] = None
    # costs3: Optional[float] = None
    currency: Optional[str] = None

    class Config:
        from_attributes = True
