
"""
This module defines a set of API endpoints for CRUD operations on a "Client" resource using the FastAPI framework and SQLAlchemy for database operations.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError
from typing import List
from api.core.database import db
from api.models.modalClientDevices import client_device_association
from api.models.modalClients import (
    Client, ClientCreate, ClientUpdate, ClientDB
)
from api.core.dependencies import get_authorization_token


router = APIRouter()


@router.get("/clients/", response_model=List[Client])
async def get_clients(skip: int = 0, limit: int = 100, sess: Session = Depends(db.get_db)):
    query = select(ClientDB).offset(skip).limit(limit)
    print(query)
    resp = await db.run_query(query, db=sess)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    return resp.data
    res = []
    res = [row for row in resp.data]
    print(res)
    for row in resp.data:
        f = Client.model_validate(row)
        print('=====')
        print(f)
    raise HTTPException(200, 'asas')
    # co_model = Client.model_validate(resp.data[0])
    # print(co_model)
    # user = Client(**resp.data[0])
    # # items = [Client(__root__=row.__dict__) for row in resp.data]
    # print(user)
    # r = Client(**resp.data)

    # result = []
    # for row in resp.data:
    #     print(type(row))
    #     print(row)

    # d = row.__dict__
    # print(d)
    # c = Client(name=row['name'], email=row['email'])
    # print(c)
    # result.append(c)
    # print(result)
    # raise HTTPException(resp.code, detail=resp.data)

    return resp.data


@router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: int):
    query = select(ClientDB).filter(ClientDB.id == client_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    return resp.data[0]


@router.post("/clients/", response_model=Client)
async def post_client(data: ClientCreate):

    update_data = data.model_dump(exclude_unset=True)
    print(update_data)

    query = select(ClientDB).filter(ClientDB.email == data.email)
    resp = await db.run_query(query)
    if resp.code == 200:
        raise HTTPException(status_code=400, detail="Email already registered")

    if resp.code == 404:
        query = insert(ClientDB).values(update_data).returning(ClientDB)
        resp = await db.run_query(query)
        if resp.code != 200:
            raise HTTPException(status_code=resp.code, detail=resp.message)

        return resp.data[0]

    raise HTTPException(status_code=resp.code, detail=resp.message)


@router.put("/clients/{client_id}", response_model=Client)
async def put_client(client_id: int, data: ClientUpdate, sess: Session = Depends((db.get_db))):

    update_data = data.model_dump(exclude_unset=True)

    query = select(ClientDB).filter(ClientDB.id == client_id)
    resp = await db.run_query(query, db=sess)
    if resp.code == 404:
        raise HTTPException(status_code=resp.code,
                            detail=f"Client ({client_id}) not found")

    query = (
        update(ClientDB).
        where(ClientDB.id == client_id).
        values(update_data)
    ).returning(ClientDB)

    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return resp.data[0]


@router.delete("/clients/{client_id}", response_model=dict)
async def del_client(client_id: int):
    query = select(ClientDB).filter(ClientDB.id == client_id)
    resp = await db.run_query(query)
    if resp.code != 200:
        raise HTTPException(resp.code, detail='client not found')

    query = (
        client_device_association.delete().where(
            client_device_association.c.client_id == client_id
        )
    )
    resp = await db.run_query(query)

    if resp.code != 404 and resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)

    query = (
        delete(ClientDB).
        where(ClientDB.id == client_id)
    )

    resp = await db.run_query(query)

    if resp.code != 200:
        raise HTTPException(status_code=resp.code, detail=resp.message)

    return {"message": 'client deleted'}
