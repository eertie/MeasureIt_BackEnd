from sqlalchemy import Column, Integer, String, func, Column, DateTime, Date, Integer, String, and_, or_, not_
from pydantic import BaseModel, ConfigDict, constr
from typing import Optional
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from api import logger
from api.core.config import AppConfig
from api.models.modalBase import Base
from api.core.utils import AppResponse
from api.models.modalClientDevices import client_device_association
from api.models.modalClientUsers import client_user_association
from api.models.modalDevices import DeviceDB


class ClientDB(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(50), index=True, unique=True)
    phone = Column(String(50), default=None)
    address = Column(String(50), default=None)
    zipcode = Column(String(50), default=None)
    place = Column(String(50), default=None)
    country = Column(String(100), default=None)
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())
    # devices = relationship("DeviceDB")
    # users = relationship("UserDB")
    devices = relationship(
        "DeviceDB", secondary=client_device_association, back_populates="clients")
    users = relationship(
        "UserDB", secondary=client_user_association, back_populates="clients")

    def __repr__(self):
        return f"<ClientDB id={self.id}, name= {self.name} mail={self.email}, created={self.timeCreated}>"


class Client(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: constr(max_length=50)
    email: str
    phone:  Optional[str] = None
    address: Optional[str] = None
    zipcode: Optional[str] = None
    place: Optional[str] = None


class ClientCreate(BaseModel):
    name: str
    email: str
    phone:  Optional[str] = None
    address: Optional[str] = None
    zipcode: Optional[str] = None
    place: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True  # Enable automatic attribute mapping


class ClientUpdate(ClientCreate):
    name: Optional[str] = None
    email: Optional[str] = None
