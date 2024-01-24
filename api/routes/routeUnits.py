from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from typing import List
from api.models.modalUnits import UnitDB, UnitCreate, Unit, UnitUpdate
from api.core.dependencies import get_authorization_token
from api.core.database import db

router = APIRouter()


@router.get("/units/", response_model=List[Unit])
# , session: Session = Depends(db.get_db)):
async def get_units(skip: int = 0, limit: int = 100):
    query = select(UnitDB).offset(skip).limit(limit)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    return resp.data


@router.get("/units/{unit_id}", response_model=Unit)
async def get_unit_by_id(unit_id: int):
    query = select(UnitDB).filter(UnitDB.id == unit_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    return resp.data[0]


@router.post("/units/", response_model=Unit)
async def create_unit(data: UnitCreate):
    query = select(UnitDB).filter(UnitDB.name == data.name)

    resp = await db.run_query(query)
    if resp.code == 200:
        raise HTTPException(
            status_code=400, detail="Unit already exists")

    if resp.code == 404:
        query = insert(UnitDB).values(
            name=data.name,
            displayName=data.displayName
        ).returning(UnitDB)
        resp = await db.run_query(query)
        if resp.code != 200:
            raise HTTPException(status_code=resp.code, detail=resp.message)

        return resp.data[0]

    raise HTTPException(status_code=resp.code, detail=resp.message)


@router.put("/units/{unit_id}", response_model=Unit)
async def update_unit(unit_id: int, data: UnitUpdate):

    query = select(UnitDB).filter(UnitDB.id == unit_id)
    resp = await db.run_query(query)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Unit ({unit_id}) not found")

    query = (
        update(UnitDB).
        where(UnitDB.id == unit_id).
        values(
            name=data.name,
            displayName=data.displayName
        )
    ).returning(UnitDB)

    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return resp.data[0]


@router.delete("/units/{unit_id}", response_model=dict)
async def delete_unit(unit_id: int):
    query = select(UnitDB).filter(UnitDB.id == unit_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    query = (
        delete(UnitDB).
        where(UnitDB.id == unit_id)
    )

    resp = await db.run_query(query)

    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail="Unit not found")

    return {"message": resp.message}
