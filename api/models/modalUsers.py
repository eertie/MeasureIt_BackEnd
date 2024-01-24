# User model
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, func, JSON, Date, Boolean, Text, Column, DateTime, Date, Integer, String, Numeric
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from api.core.config import AppConfig
from api.core.utils import AppResponse
from api.models.modalBase import Base
from api.models.modalClientUsers import client_user_association


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(50))
    name = Column(String(50), nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String(50), default=None)
    facebook_id = Column(String, unique=True, index=True)
    google_id = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())
    clients = relationship(
        "ClientDB", secondary=client_user_association, back_populates="users")
