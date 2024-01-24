import sys
import datetime
from typing import List, Set, Dict, Tuple, Optional
from sqlalchemy import inspect
from sqlalchemy.sql import text
from inspect import getmembers
from api.core.utils import jsonEncoder, AppResponse
from api.models.modalSignals import SignalDB
from api.models.modalTariffs import TariffDB
from api.models.modalMeasurements import MeasurementDB
from api.core.config import AppConfig
from api.core.database import db


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


async def createTriggers():

    sqlFillTariffId = '''
       CREATE OR REPLACE FUNCTION public.fill_tariff_id()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        DECLARE	
            tariff_id integer;        
            BEGIN
                if NEW.tariff_id is null then
                  select id into tariff_id from tariffs where signal_id = NEW.signal_id and NEW.datetime >= tariffs."startDate" order by tariffs."startDate" desc limit 1;
                  if tariff_id is not null then
                    NEW.tariff_id = tariff_id;
                  else
                     -- point to null tariff record --> maybe insert a new taiff record? 
                    NEW.tariff_id = 0;

                  end if;                   
                end if;
                RETURN NEW; 
            END;
        $function$
    '''

    sqlFillTariffIdTrigger = '''
        --DROP TRIGGER if exists get_tariff_id ON public.measurements;
        CREATE OR REPLACE TRIGGER get_tariff_id
        BEFORE INSERT ON public.measurements
        FOR EACH ROW
        EXECUTE FUNCTION fill_tariff_id();    
    '''

    sqlFillMeasurementDisplayName = '''
       CREATE OR REPLACE FUNCTION public.fill_measurement_displayname()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        DECLARE	
            field_name character varying;
            unit character varying;
            BEGIN
                if NEW."displayName" is null then                  
                  select a.name, b.name into field_name, unit from signals a
                  inner join units b on a.unit_id = b.id where a.id = NEW.signal_id;

                  if field_name is not null then                    
                    NEW."displayName" = concat(field_name, ' [', unit, ']');
                  end if;                   
                end if;
                RETURN NEW; 
            END;
        $function$
    '''

    sqlFillMeasurementDisplayNameTrigger = '''
        --DROP TRIGGER if exists fill_measurement_fieldname ON public.measurements;
        CREATE OR REPLACE TRIGGER fill_measurement_displayname
        BEFORE INSERT ON public.measurements
        FOR EACH ROW
        EXECUTE FUNCTION fill_measurement_displayname();
    '''

    r = await db.run_query(text(sqlFillMeasurementDisplayName))
    r = await db.run_query(text(sqlFillMeasurementDisplayNameTrigger))
    # r = await db.run_query(text(sqlFillTariffId))
    # r = await db.run_query(text(sqlFillTariffIdTrigger))

    return r


async def populateDB() -> AppResponse:
    try:
        await db.run_query(text(f"ALTER USER {AppConfig.db_user} SET timezone='{AppConfig.db_timezone}';"))
        await db.run_query(text(f"insert into clients (email, name) values('test@gmail.com', 'companyX')"))

        await db.run_query(text(f'insert into units ("name", "displayName") values(\'KwH\', \'Kilowatt hour\')'))
        await db.run_query(text(f'insert into units ("name", "displayName") values(\'m3\', \'Cubic metre\')'))
        await db.run_query(text(f'insert into units ("name", "displayName") values(\'L/M\', \'Liters per min\')'))
        await db.run_query(text(f'insert into units ("name", "displayName") values(\'W\', \'Watt\')'))
        await db.run_query(text(f'insert into units ("name", "displayName") values(\'kW\', \'KiloWatt\')'))

        await db.run_query(text(f'insert into devices ("name", "location", "is_active") values(\'P1 meter\', \'meterkast\', true)'))
        await db.run_query(text(f'insert into client_devices ("client_id", "device_id") values(1,1)'))

        await db.run_query(text(f'insert into signals ("device_id", "unit_id", "name") values( 1, 2, \'gas\')'))
        await db.run_query(text(f'insert into signals ("device_id", "unit_id", "name") values( 1, 1, \'import low\')'))
        await db.run_query(text(f'insert into signals ("device_id", "unit_id", "name") values( 1, 1, \'import high\')'))
        await db.run_query(text(f'insert into signals ("device_id", "unit_id", "name") values( 1, 1, \'export low\')'))
        await db.run_query(text(f'insert into signals ("device_id", "unit_id", "name") values( 1, 1, \'export high\')'))

        return AppResponse(200, 'succes', {'mesage': 'database populated'})
    except Exception as e:
        return AppResponse(500, 'error', {'mesage': 'error populating database'})
