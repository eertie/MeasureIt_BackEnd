
import inspect
from functools import lru_cache
from sqlalchemy import create_engine, select, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.sql.dml import Insert, Update
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import IntegrityError
from api.core.config import AppConfig
from api import logger
from api.models.modalBase import Base
from api.core.utils import AppResponse
# from icecream import ic
from api.models.modalDevices import (Device)


class Database:

    _instance = None

    def __init__(self, appConfig: AppConfig, appDebug=False):
        if Database._instance is not None:
            raise Exception(
                "Singleton class cannot be instantiated more than once!")
        else:
            Database._instance = self

        self.appConfig = appConfig
        self.useAsync = appConfig.db_useAsync
        self.debug = appConfig.db_debug or appDebug

        if self.useAsync:
            # self.db = databases.Database(AppConfig.db_url_async)
            self.engine = create_async_engine(
                self.appConfig.db_url_async, echo=self.appConfig.db_debug,  future=True)

            self.sess_async = sessionmaker(bind=self.engine,  autocommit=False, autoflush=False,
                                           class_=AsyncSession, expire_on_commit=False)
        else:
            # self.db = databases.Database(self.appConfig.db_url_local)
            self.engine = create_engine(
                self.appConfig.db_url_local, echo=self.appConfig.db_debug)
            self.sess_local = sessionmaker(
                bind=self.engine, autocommit=False, autoflush=False)

        self.metadata = MetaData()
        self.metadata.bind = self.engine
        self.metadata.info['tzinfo'] = True

    @asynccontextmanager
    async def get_async_session(self):
        session = self.sess_async()
        try:
            # ic('------ session yield')
            yield session
        except:
            # await session.rollback()
            raise
        finally:
            # ic('------ session closed')
            await session.close()

    @contextmanager
    def get_sync_session(self):
        session = self.sess_local()
        try:
            yield session
        except:
            raise
        finally:
            session.close()

    def get_db(self):
        if self.useAsync:
            return self.get_async_session()
        else:
            return self.get_sync_session()

    async def connect(self):
        if self.useAsync:
            await self.engine.connect()
        else:
            self.engine.connect()

    async def disconnect(self):
        if self.useAsync:
            await self.engine.dispose()
        else:
            self.engine.dispose()

    async def run_query(self, query, db=None, returnAsDict=False, returnAsSession=False) -> AppResponse:

        def handleSelectReturn(query):
            try:
                rows = result.all()
                count = len(rows)
                if count <= 0:
                    return AppResponse(404, 'nothing found', data=rows)
                else:
                    if returnAsDict:
                        rows = [item._mapping for item in rows]
                    else:
                        rows = [row[0] for row in rows]

                    return AppResponse(data=rows)

            except Exception as e:
                return AppResponse(500, 'error parsing SQL select stmt', data=None, e=e)

        session = None
        if self.debug:
            caller = inspect.currentframe().f_back.f_code
            logger.debug(
                f"Database.run_query() called from {caller.co_filename} at line {caller.co_firstlineno}")

        try:
            if not db:
                db = self.get_db()

            objIsSelect = isinstance(query, Select)
            objIsInsert = isinstance(query, Insert)
            objIsUpdate = isinstance(query, Update)

            if self.useAsync:
                async with db as session:
                    if self.debug:
                        logger.debug(query)

                    result = await session.execute(query)

                    if returnAsSession:
                        return AppResponse(200, 'success', data=result)

                    if isinstance(query, Select):
                        return handleSelectReturn(result)
                    else:
                        # if result.rowcount <= 0:
                        #     return AppResponse(404, 'nothing found', data=None)
                        rows = None
                        await session.commit()
                        if objIsInsert or objIsUpdate:
                            rows = result.all()
                            if returnAsDict:
                                rows = [item for item in rows]

                        return AppResponse(200, 'success', data=rows)
            else:
                with db as session:
                    result = session.execute(query)
                    if returnAsSession:
                        return AppResponse(200, 'success', data=result)
                    if objIsSelect:
                        return handleSelectReturn(result)
                    else:
                        if result.rowcount <= 0:
                            return AppResponse(404, 'nothing found', data=None)
                        session.commit()
                        if objIsInsert or objIsUpdate:
                            rows = result.all()
                            if returnAsDict:
                                rows = [item for item in rows]
                        return AppResponse(200, 'success', data=rows)

        except IntegrityError as e:
            if session is not None:
                await session.rollback() if self.useAsync else session.rollback()
            err = str(e).split(':')[1].strip()
            err = err.split('\n')[0]
            return AppResponse(400, f'IntegrityError: {err}', e.orig.__dict__)

        except Exception as e:
            if session is not None:
                await session.rollback() if self.useAsync else session.rollback()
            try:
                err = str(e).split(':')[1].strip()
            except:
                err = str(e)

            return AppResponse(500, str(err), None, e)

        # finally: already done in get_db
        #     await session.close() if self.useAsync else session.close()

    async def createDatabase(self, checkfirst=True) -> AppResponse:
        try:
            if self.useAsync:
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all, checkfirst=checkfirst)
            else:
                Base.metadata.create_all(self.engine, checkfirst=checkfirst)

            Base.metadata.info['tzinfo'] = True  # enable timezone support
            await self.run_query(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            await self.run_query(text(f"ALTER USER {AppConfig.db_user} SET timezone='{AppConfig.db_timezone}';"))
            return AppResponse(200, 'success')
        except Exception as e:
            return AppResponse(500, 'Error creating database', None, e)

    async def get_table_counts(self, session):
        async with self.engine.begin() as conn:
            try:
                async with conn.begin():
                    connection = conn.connection
                    inspector = inspect(connection)
                    table_counts = []
                    for table_name in inspector.get_table_names():
                        table = inspector.get_table(table_name)
                        result = await session.execute(table.select().limit(1))
                        has_records = result.fetchone() is not None
                        table_counts.append(
                            {"table_name": table_name, "record_count": 1 if has_records else 0})

                    return table_counts

            except Exception as e:
                print(
                    f"An error occurred while retrieving table counts: {str(e)}")

    async def clearDatabase(self, checkfirst=True) -> AppResponse:
        try:
            sess = self.get_db()
            # list = await self.get_table_counts(sess)

            if self.useAsync:
                if checkfirst:
                    query = select(text('count(*) from devices'))
                    resp = await self.run_query(query, db=sess)
                    device_count = resp.data[0]
                    if device_count > 0:
                        return AppResponse(403, 'Database is not empty!')

                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.drop_all, checkfirst=checkfirst)
                    await conn.run_sync(Base.metadata.create_all)
            else:
                Base.metadata.drop_all(self.engine, checkfirst=checkfirst)
                Base.metadata.create_all

            return AppResponse(200, 'Database successfully cleared', data={'status': 'Database successfully cleared'})

        except Exception as e:
            return AppResponse(500, 'Error clearing database', e=e)

    async def getSQLVersion(self) -> AppResponse:
        sess = self.get_db()
        query = select(text('version() as version'))
        resp = await self.run_query(query, db=sess)
        return AppResponse(resp.code, resp.message, resp.data[0])

    async def getSQLLocations(self) -> AppResponse:
        sess = self.get_db()
        query = select(
            text("name, setting FROM pg_settings WHERE category = 'File Locations';"))
        resp = await self.run_query(query, db=sess, returnAsDict=True)
        return AppResponse(resp.code, resp.message, resp.data)


db = Database(AppConfig, AppConfig.app_debug == True)
