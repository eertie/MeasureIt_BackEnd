# from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, func, JSON, Date, Boolean, Text, Column, DateTime, Date, Integer, String, Numeric
from sqlalchemy import Column, Integer, String, Text, Boolean, func,  DateTime, Date, and_, or_, not_
from pydantic import BaseModel, ValidationError, Field
from typing import Optional
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from geoalchemy2.functions import ST_AsGeoJSON
from api.models.modalClientDevices import client_device_association
from api.models.modalGeoLocation import GeoLocation, geoToDict
from api.core.config import AppConfig
from api.models.modalBase import Base
from api.core.utils import AppResponse


class DeviceDB(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(Text)
    location = Column(String(50))
    geo_point = Column(Geometry(geometry_type='POINT',
                                srid=AppConfig.db_geo_srid))
    is_active = Column(Boolean, default=True)
    timeCreated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
    timeUpdated = Column(
        DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())
    clients = relationship(
        "ClientDB", secondary=client_device_association, back_populates="devices")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'geo_point': ST_AsGeoJSON(self.geo_point),
            'is_active': self.is_active,
            'timeCreated': self.timeCreated,
            'timeUpdated': self.timeUpdated
        }


class Device(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    geo_point: Optional[GeoLocation] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True
        # arbitrary_types_allowed = True


class DeviceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    geo_point: Optional[GeoLocation] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True
        # arbitrary_types_allowed = True


class DeviceUpdate(DeviceCreate):
    name: Optional[str] = None


def makeDevice(row: dict):
    point = geoToDict(row['geo_point'])
    device = Device(id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    location=row['location'], geo_point=point,
                    is_active=row['is_active']
                    )
    return device
