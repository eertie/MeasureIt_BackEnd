import datetime
import json
import decimal
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    """Base Class"""

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
