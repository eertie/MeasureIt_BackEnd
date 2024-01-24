from fastapi import APIRouter, Depends, HTTPException

from api.core.dependencies import get_authorization_token
from api.core.database import db
from api.core.initDB import populateDB, createTriggers

router = APIRouter()


@router.post("/empty-db")
async def emptyDB(checkIfEmpty: bool):
    resp = await db.clearDatabase(checkIfEmpty)
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    respT = await createTriggers()
    return resp.data


@router.post("/populate-db")
async def populate_db():
    resp = await populateDB()
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    print(resp)
    return resp.data
