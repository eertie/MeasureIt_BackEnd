
"""
This module defines a set of API endpoints for CRUD operations on a "Measurement" resource using the FastAPI framework and SQLAlchemy for database operations.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError
from typing import List
from api.core.database import db
from api.models.modalMeasurements import (
    MeasurementDB, Measurement, MeasurementCreate, MeasurementUpdate)
from api.core.dependencies import get_authorization_token

router = APIRouter()


@router.get("/measurements/", response_model=List[Measurement])
async def get_measurements(skip: int = 0, limit: int = 100, sess: Session = Depends(db.get_db)):
    query = select(MeasurementDB).offset(skip).limit(limit)
    resp = await db.run_query(query, db=sess)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    return resp.data


@router.get("/measurements/{measurement_id}", response_model=Measurement)
async def get_measurement(measurement_id: int):
    query = select(MeasurementDB).filter(MeasurementDB.id == measurement_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    return resp.data[0]


@router.post("/measurements/", response_model=Measurement)
async def post_measurement(data: MeasurementCreate):
    update_data = data.model_dump(exclude_unset=True)
    query = insert(MeasurementDB).values(
        update_data).returning(MeasurementDB)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return resp.data[0]


@router.put("/measurements/{measurement_id}", response_model=Measurement)
async def put_measurement(measurement_id: int, data: MeasurementUpdate, sess: Session = Depends((db.get_db))):

    update_data = data.model_dump(exclude_unset=True)

    query = select(MeasurementDB).filter(MeasurementDB.id == measurement_id)
    resp = await db.run_query(query, db=sess)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Measurement ({measurement_id}) not found")

    query = (
        update(MeasurementDB).
        where(MeasurementDB.id == measurement_id).
        values(update_data)
    ).returning(MeasurementDB)

    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return resp.data[0]


@router.delete("/measurements/{measurement_id}", response_model=dict)
async def del_measurement(measurement_id: int):
    query = select(MeasurementDB).filter(MeasurementDB.id == measurement_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail='measurement not found')

    if resp.code != 404 and resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    query = (
        delete(MeasurementDB).
        where(MeasurementDB.id == measurement_id)
    )

    resp = await db.run_query(query)

    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return {"message": 'measurement deleted'}
