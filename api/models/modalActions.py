from sqlalchemy import ForeignKey, func, JSON, Date, Boolean, Text, Column, DateTime, Date, Integer, String, Numeric
from sqlalchemy.dialects.postgresql import MONEY
from sqlalchemy.sql import text
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import synonym
from sqlalchemy.orm import relationship
from api.core.config import AppConfig
from api.models.modalBase import Base


class ActionsDB(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    type = Column(String(50))  # trigger, cron
    description = Column(Text)
    measurement_id = Column(Integer)
    cronmask = Column(String(50))
    startProgram = Column(String)
    programParameters = Column(JSON)
    timeoutSeconds = Column(Integer)
    startTime = Column(DateTime(timezone=AppConfig.db_useTimeZone))
    active = Column(Boolean)
    pid = Column(Integer)
    endTime = Column(DateTime(timezone=AppConfig.db_useTimeZone))
    exitStatus = Column(Integer)
    exitStatusJson = Column(JSON)
    startNextAction_id = Column(Integer)
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())
