from sqlalchemy import Column, Integer, Table, ForeignKey
from .modalBase import Base

# https://medium.com/@warrenzhang17/many-to-many-relationships-in-sqlalchemy-ba08f8e9ccf7

client_user_association = Table(
    'client_users',
    Base.metadata,
    Column('client_id', Integer, ForeignKey('clients.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)
