from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, func, JSON, Date, Boolean, Text, Column, DateTime, Date, Integer, String, Numeric
# from sqlalchemy.ext.declarative import declarative_base
from api.core.config import AppConfig
from api.models.modalBase import Base


class RemarkDB(Base):
    __tablename__ = "remarks"
    id = Column(Integer, primary_key=True, index=True)
    remark = Column(String)
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())
