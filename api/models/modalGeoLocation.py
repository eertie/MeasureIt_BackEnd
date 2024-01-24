from pydantic import BaseModel
from geoalchemy2.shape import to_shape
from shapely import geometry
from geoalchemy2.shape import from_shape, to_shape


class GeoLocation(BaseModel):
    latitude: float
    longitude: float


def geoToDict(dbField):
    p = geometry.mapping(to_shape(dbField))
    point = p['coordinates']
    if point:
        longitude = float(point[0])
        latitude = float(point[1])
        geo = GeoLocation(latitude=latitude, longitude=longitude)
        return geo
    else:
        print("Invalid POINT geometry format")
        return {}
