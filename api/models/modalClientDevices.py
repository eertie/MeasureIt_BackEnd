from sqlalchemy import Column, Integer, Table, ForeignKey,  PrimaryKeyConstraint
from api.models.modalBase import Base

# https://medium.com/@warrenzhang17/many-to-many-relationships-in-sqlalchemy-ba08f8e9ccf7


client_device_association = Table(
    'client_devices',
    Base.metadata,
    Column('client_id', Integer, ForeignKey('clients.id', ondelete='CASCADE')),
    Column('device_id', Integer, ForeignKey('devices.id', ondelete='CASCADE')),
    PrimaryKeyConstraint('client_id', 'device_id')
)
