from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, delete
from typing import List
from api.models.modalDevices import (
    DeviceDB, Device, DeviceCreate, DeviceUpdate, makeDevice

)
from api.core.dependencies import get_authorization_token
from api.core.database import db

router = APIRouter()


@router.get("/devices/", response_model=List[Device])
async def get_devices(skip: int = 0, limit: int = 100):
    query = select(DeviceDB).offset(skip).limit(limit)
    resp = await db.run_query(query, returnAsDict=False)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    rows = [makeDevice(row.as_dict()) for row in resp.data]
    return rows


@router.get("/devices/{device_id}", response_model=Device)
async def get_device(device_id: int) -> Device:
    query = select(DeviceDB).filter(DeviceDB.id == device_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    row = [r.as_dict() for r in resp.data][0]

    return makeDevice(row)


@router.post("/devices/", response_model=Device)
async def post_device(data: DeviceCreate):

    update_data = data.model_dump(exclude_unset=True)

    query = select(DeviceDB).filter(DeviceDB.name == data.name)
    resp = await db.run_query(query)
    if resp.code == 200:
        raise HTTPException(
            status_code=400, detail="Device name already exists")

    if resp.code == 404:
        if data.geo_point:
            lon = data.geo_point.longitude
            lat = data.geo_point.latitude
            point = f"POINT({lon} {lat})"
            update_data['geo_point'] = point

        query = insert(DeviceDB).values(update_data).returning(DeviceDB)

        resp = await db.run_query(query)

        if resp.code != 200:
            raise HTTPException(status_code=resp.code, detail=resp.message)

        return makeDevice(resp.data[0])

    raise HTTPException(status_code=resp.code, detail=resp.message)


@router.put("/devices/{device_id}", response_model=Device)
async def put_device(device_id: int, data: DeviceUpdate):

    update_data = data.model_dump(exclude_unset=True)
    query = select(DeviceDB).filter(DeviceDB.id == device_id)
    resp = await db.run_query(query)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Device ({device_id}) not found")

    if data.geo_point:
        lon = data.geo_point.longitude
        lat = data.geo_point.latitude
        point = f"POINT({lon} {lat})"
        update_data['geo_point'] = point

    query = (update(DeviceDB).
             where(DeviceDB.id == device_id).
             values(update_data).returning(DeviceDB)
             )

    resp = await db.run_query(query)

    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return makeDevice(resp.data[0])


@router.delete("/devices/{device_id}", response_model=dict)
async def delete_device(device_id: int):
    query = select(DeviceDB).filter(DeviceDB.id == device_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    query = (
        delete(DeviceDB).
        where(DeviceDB.id == device_id)
    )

    resp = await db.run_query(query)

    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail="Device not found")

    return {"message": resp.message}
