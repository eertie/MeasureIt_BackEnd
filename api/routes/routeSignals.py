from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, delete
from typing import List
from sqlalchemy.sql import text
from sqlalchemy.orm import Session, joinedload
from api.core.database import db
from api.models.modalDevices import DeviceDB
from api.models.modalUnits import UnitDB
from api.models.modalSignals import SignalDB, Signal, SignalUpdate, SignalCreate
from api.core.dependencies import get_authorization_token

router = APIRouter()


@router.get("/signals/", response_model=List[dict])
async def get_signals(skip: int = 0, limit: int = 100, sess: Session = Depends(db.get_db)):
    query = select(SignalDB.id,
                   SignalDB.name.label('signal_name'),
                   SignalDB.description.label('signal_description'),
                   DeviceDB.id.label('device_id'),
                   DeviceDB.name.label('devicename'),
                   DeviceDB.description.label('device_description'),
                   UnitDB.id.label('unit_id'),
                   UnitDB.name.label('unit_name'),
                   UnitDB.displayName.label('unit_displayname'))\
        .outerjoin(DeviceDB, DeviceDB.id == SignalDB.device_id)\
        .outerjoin(UnitDB, UnitDB.id == SignalDB.unit_id)\
        .offset(skip).limit(limit)

    resp = await db.run_query(query, returnAsDict=True)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    rows = resp.data
    return rows


@router.get("/signals/{signal_id}", response_model=Signal)
async def get_signals_by_id(signal_id: int):
    query = select(SignalDB).filter(SignalDB.id == signal_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    return resp.data[0]


@router.post("/signals/", response_model=Signal)
async def create_signal(data: SignalCreate):

    # Exclude fields not set in the request
    update_data = data.model_dump(exclude_unset=True)

    if data.device_id:
        query = select(DeviceDB).filter(DeviceDB.id == data.device_id)
        resp = await db.run_query(query)
        if resp.code != 200:
            raise HTTPException(status_code=400, detail="Device not found")

    if data.unit_id:
        query = select(UnitDB).filter(UnitDB.id == data.unit_id)
        resp = await db.run_query(query)
        if resp.code != 200:
            raise HTTPException(status_code=400, detail="Unit not found")

    query = select(SignalDB).filter(SignalDB.name == data.name,
                                    SignalDB.device_id == data.device_id,
                                    SignalDB.unit_id == data.unit_id)

    resp = await db.run_query(query)
    if resp.code == 200:
        raise HTTPException(
            status_code=400, detail="Signal already Exists (name, unit and device combination must be unique)")

    if resp.code == 404:
        query = insert(SignalDB).values(update_data).returning(SignalDB)
        resp = await db.run_query(query)
        if resp.code != 200:
            raise HTTPException(status_code=resp.code, detail=resp.message)

        return resp.data[0]

    raise HTTPException(status_code=resp.code, detail=resp.message)


@router.put("/signals/{signal_id}", response_model=Signal)
async def update_signal(signal_id: int, data: SignalUpdate):

    update_data = data.model_dump(exclude_unset=True)

    if data.device_id:
        query = select(DeviceDB).filter(DeviceDB.id == data.device_id)
        resp = await db.run_query(query)
        if resp.code != 200:
            raise HTTPException(status_code=400, detail="Device not found")

    if data.unit_id:
        query = select(UnitDB).filter(UnitDB.id == data.unit_id)
        resp = await db.run_query(query)
        if resp.code != 200:
            raise HTTPException(status_code=400, detail="Unit not found")

    query = select(SignalDB).filter(SignalDB.id == signal_id)
    resp = await db.run_query(query)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Signal ({signal_id}) not found")

    query = (
        update(SignalDB).
        where(SignalDB.id == signal_id).
        values(update_data)
    ).returning(SignalDB)

    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return resp.data[0]


@router.delete("/signals/{signal_id}", response_model=dict)
async def delete_signal(signal_id: int):
    query = select(SignalDB).filter(SignalDB.id == signal_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    query = (
        delete(SignalDB).
        where(SignalDB.id == signal_id)
    )

    resp = await db.run_query(query)

    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail="Signal not found")

    return {"message": resp.message}
