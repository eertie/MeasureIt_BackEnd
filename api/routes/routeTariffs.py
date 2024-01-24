from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete, func
from typing import List
from api.models.modalTariffs import (
    TariffDB, TariffCreate, Tariff, TariffUpdate

)
from api.models.modalSignals import SignalDB
from api.models.modalDevices import DeviceDB
from api.models.modalUnits import UnitDB

from api.core.dependencies import get_authorization_token
from api.core.database import db


router = APIRouter()


@router.get("/tariffs/", response_model=List[dict])
async def get_tariffs(skip: int = 0, limit: int = 100,  sess: Session = Depends(db.get_db)):

    query = select(
        TariffDB.id,
        TariffDB.startDate,
        TariffDB.remark,
        # func.round(TariffDB.costs1, 5).label('costs'),
        TariffDB.unit_cost1.label('unit_cost'),
        # TariffDB.unit_cost2.label('unit_cost2'),
        # TariffDB.unit_cost3.label('unit_cost3'),
        TariffDB.currency,
        SignalDB.id.label('signal_id'),
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
        .join(TariffDB, TariffDB.signal_id == SignalDB.id)\
        .offset(skip).limit(limit)

    resp = await db.run_query(query, returnAsDict=True)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    rows = resp.data
    return rows


@router.get("/tariffs/{tariff_id}", response_model=Tariff)
async def get_tariff(tariff_id: int) -> Tariff:
    query = select(TariffDB).filter(TariffDB.id == tariff_id)
    resp = await db.run_query(query, returnAsSession=True)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    row = [dict(row) for row in resp.data][0]
    print(row)
    raise HTTPException(200)

    row['unit_cost'] = row['unit_cost1']
    row.pop('unit_cost1')
    return row


@router.post("/tariffs/", response_model=Tariff)
async def post_tariff(data: TariffCreate):
    update_data = data.model_dump(exclude_unset=True)
    # Convert string to date object
    # update_data['startDate'] = datetime.fromisoformat(str(data.startDate))
    #  sdt = datetime(2023, 2, 15, 12, 0, 0)
    update_data['unit_cost1'] = update_data['unit_cost']
    update_data.pop('unit_cost')
    query = insert(TariffDB).values(update_data).returning(TariffDB)
    resp = await db.run_query(query, returnAsSession=True)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    row = [dict(row) for row in resp.data][0]
    row['unit_cost'] = row['unit_cost1']
    row.pop('unit_cost1')
    return row


@router.put("/tariffs/{tariff_id}", response_model=Tariff)
async def put_tariff(tariff_id: int, data: TariffUpdate):
    query = select(TariffDB).filter(TariffDB.id == tariff_id)
    resp = await db.run_query(query)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Tariff ({tariff_id}) not found")

    update_data = data.model_dump(exclude_unset=True)
    query = (
        update(TariffDB).
        where(TariffDB.id == tariff_id).
        values(update_data)
    ).returning(TariffDB)

    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return resp.data[0]


@router.delete("/tariffs/{tariff_id}", response_model=dict)
async def delete_tariff(tariff_id: int):
    query = select(TariffDB).filter(TariffDB.id == tariff_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    query = (
        delete(TariffDB).
        where(TariffDB.id == tariff_id)
    )

    resp = await db.run_query(query)

    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail="Tariff not found")

    return {"message": resp.message}
