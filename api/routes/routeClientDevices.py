

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from typing import List
from api.models.modalClients import ClientDB
from api.models.modalDevices import DeviceDB, Device, makeDevice
from api.models.modalClientDevices import client_device_association
from api.core.dependencies import get_authorization_token
from api.core.database import db

router = APIRouter()


@router.get("/client/{client_id}/devices", response_model=List[Device])
async def get_devices_by_client(client_id: int, sess: Session = Depends(db.get_db)):

    query = select(ClientDB).filter(ClientDB.id == client_id)
    resp = await db.run_query(query, db=sess)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Client ({client_id}) not found")

    query = select(ClientDB).options(joinedload(
        ClientDB.devices)).filter_by(id=client_id)

    resp = await db.run_query(query, returnAsSession=True)

    client = resp.data.scalars().unique().first()

    if not client:
        raise HTTPException(404, detail='No devices assigned for this client')

    rows = [makeDevice(row.as_dict()) for row in client.devices]

    if len(rows) == 0:
        raise HTTPException(404, detail='No devices assigned for this client')

    return rows


@router.post("/client/{client_id}/device/{device_id}")
async def associate_device_with_client(client_id: int, device_id: int, sess: Session = Depends(db.get_db)):

    query = select(DeviceDB).filter(DeviceDB.id == device_id)
    resp = await db.run_query(query)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Device not found")

    query = select(ClientDB).filter(ClientDB.id == client_id)
    resp = await db.run_query(query)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Client ({client_id}) not found")

    query = select(client_device_association).where(
        and_(
            client_device_association.c.client_id == client_id,
            client_device_association.c.device_id == device_id
        ))

    resp = await db.run_query(query)
    if resp.code == 200:
        raise HTTPException(
            status_code=400, detail='client device already exixts')

    query = insert(client_device_association).values(
        client_id=client_id, device_id=device_id).returning(client_device_association)

    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return resp.data[0]


@router.delete("/client/{client_id}/device/{device_id}")
async def disassociate_device_from_client(client_id: int, device_id: int, sess: Session = Depends(db.get_db)):

    query = select(DeviceDB).filter(DeviceDB.id == device_id)
    resp = await db.run_query(query)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Device not found")

    query = select(ClientDB).filter(ClientDB.id == client_id)
    resp = await db.run_query(query)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Client ({client_id}) not found")

    query = delete(client_device_association).where(
        client_device_association.c.client_id == client_id, client_device_association.c.device_id == device_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code,
                            detail="Client Device association not found")
    return {"message": resp.message}
