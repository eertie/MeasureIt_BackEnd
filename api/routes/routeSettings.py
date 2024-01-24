from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from typing import List
from api.models.modalSettings import (
    Setting, SettingDB, SettingCreate, SettingUpdate

)
from api.core.dependencies import get_authorization_token
from api.core.database import db
from api.core.initDB import populateDB

router = APIRouter()


@router.get("/settings/", response_model=List[Setting])
# , session: Session = Depends(db.get_db)):
async def get_settings(skip: int = 0, limit: int = 100,  sess: Session = Depends(db.get_db)):
    query = select(SettingDB).offset(skip).limit(limit)
    resp = await db.run_query(query, db=sess)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    rows = resp.data
    return rows


@router.get("/settings/{setting_id}", response_model=Setting)
async def get_setting(setting_id: int) -> Setting:
    query = select(SettingDB).filter(SettingDB.id == setting_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    return resp.data[0]


@router.post("/settings/", response_model=Setting)
async def post_setting(data: SettingCreate):
    query = select(SettingDB).filter(SettingDB.name == data.name)
    resp = await db.run_query(query)
    if resp.code == 200:
        raise HTTPException(
            status_code=400, detail="Setting name already exists")

    if resp.code == 404:
        query = insert(SettingDB).values(
            name=data.name, value=data.value).returning(SettingDB)
        resp = await db.run_query(query)
        if resp.code != 200:
            raise HTTPException(status_code=resp.code, detail=resp.message)

        return resp.data[0]

    raise HTTPException(status_code=resp.code, detail=resp.message)


@router.put("/settings/{setting_id}", response_model=Setting)
async def put_setting(setting_id: int, data: SettingUpdate):
    query = select(SettingDB).filter(SettingDB.id == setting_id)
    resp = await db.run_query(query)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Setting ({setting_id}) not found")

    query = (
        update(SettingDB).
        where(SettingDB.id == setting_id).
        values(
            name=data.name,
            value=data.value
        )
    ).returning(SettingDB)

    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return resp.data[0]


@router.delete("/settings/{setting_id}", response_model=dict)
async def delete_setting(setting_id: int):
    query = select(SettingDB).filter(SettingDB.id == setting_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    query = (
        delete(SettingDB).
        where(SettingDB.id == setting_id)
    )

    resp = await db.run_query(query)

    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail="Setting not found")

    return {"message": resp.message}
