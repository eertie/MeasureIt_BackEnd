import uvicorn
import time
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, Depends, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api import logger
from api.core.config import AppConfig, getAppInfo
from api.routes.routeSettings import router as settings_router
from api.routes.routeClients import router as clients_router
from api.routes.routeDevices import router as devices_router
from api.routes.routeClientDevices import router as clients_devices_router
from api.routes.routeUnits import router as unit_router
from api.routes.routeTariffs import router as tariff_router
from api.routes.routeSignals import router as signal_router
from api.routes.routeMeasurements import router as measurement_router
from api.routes.routeUtils import router as utils_router
from api.core.database import db
from api.core.initDB import createTriggers

# import debugpy
# debugpy.listen(("localhost", 5678))

app = FastAPI(debug=AppConfig.app_debug, title=AppConfig.app_title)


def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )


add_cors_middleware(app)


@app.on_event("startup")
async def startup_event():
    # await db.connect()
    resp = await db.createDatabase()
    if resp.code != 200:
        raise HTTPException(resp.code, detail=resp.message)
    respT = await createTriggers()
    return resp.data

    # info = await db.getSQLVersion()
    # logger.info(f'App Started: {info.data}')


@app.on_event("shutdown")
async def shutdown():
    # await db.disconnect()
    logger.info('App exited')


async def process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.middleware("http")(process_time_header)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    hostname = request.headers.get("host")
    return f"""
    <html>
        <head>
            <title>Measurements API</title>
        </head>
        <body>
            <h1>Welcome to Measurements API</h1>
            <p><a href="http://{hostname}/docs">See the docs for all endpoints</a></p>
        </body>
    </html>
    """


@app.get("/info")
async def app_info(sess: Session = Depends((db.get_db))):
    app_info = await getAppInfo()
    locations = await db.getSQLLocations()
    version = await db.getSQLVersion()
    app_info['database'] = {
        'version': version.data,
        'locations': locations.data
    }
    return app_info


prefix = "/api"


app.include_router(measurement_router, prefix=prefix, tags=["measurements"])
app.include_router(signal_router,  prefix=prefix, tags=["signals"])
app.include_router(tariff_router,  prefix=prefix, tags=["tariffs"])
app.include_router(clients_router, prefix=prefix, tags=["clients"])
app.include_router(devices_router, prefix=prefix, tags=["devices"])
app.include_router(clients_devices_router, prefix=prefix,
                   tags=["client_devices"])
app.include_router(unit_router,  prefix=prefix, tags=["units"])
app.include_router(settings_router, prefix=prefix, tags=["settings"])
app.include_router(utils_router, prefix=prefix, tags=["utils"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000,
                reload=True, log_level="info")
