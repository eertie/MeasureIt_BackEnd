import os
from secrets import token_urlsafe
import logging
from pytz import timezone
import toml
from pydantic import create_model
from pydantic_settings import BaseSettings
from typing import Type
from icecream import ic


class ConfigModel(BaseSettings):
    app_title: str
    app_version: str
    app_port: int
    app_debug: bool
    app_loglevel: int
    app_currency: str
    app_secret: str

    db_host: str
    db_database: str
    db_user: str
    db_password: str
    db_useAsync: bool
    db_debug: bool
    db_url_local: str
    db_url_async: str
    db_useTimeZone: bool
    db_timezone: str
    db_geo_srid: int
    db_useMaterializedViews: bool    # db_useTimeZone: bool

    @classmethod
    def from_toml(cls: Type['ConfigModel'], toml_file: str, section: str = None) -> 'ConfigModel':
        config = toml.load(toml_file)
        merged_config = {**config.get("app", {}), **config.get("database", {})}
        merged_config['app_port'] = int(os.environ.get("PORT", None))
        merged_config['app_loglevel'] = logging.DEBUG if merged_config['app_debug'] else logging.INFO
        merged_config['app_secret'] = token_urlsafe(20)
        db_host = 'db'
        db_database = os.environ.get("POSTGRES_DB", None)
        db_user = os.environ.get("POSTGRES_USER", None)
        db_password = os.environ.get("POSTGRES_PASSWORD", None)
        merged_config['db_host'] = db_host
        merged_config['db_database'] = db_database
        merged_config['db_user'] = db_user
        merged_config['db_password'] = db_password
        merged_config['db_url_local'] = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_database}'
        merged_config['db_url_async'] = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_database}'
        Model = create_model("Model", **{k: (type(v), ...)
                             for k, v in merged_config.items()})
        return Model(**merged_config)

    @classmethod
    def get_section(cls, section='app'):
        pass


AppConfig = ConfigModel.from_toml("/api/api/config.toml")

print(AppConfig.model_dump_json(indent=2))


async def getAppInfo() -> dict:

    env_vars = dict(os.environ)

    confApp = {k: v for k, v in AppConfig.__dict__.items()
               if not k.startswith("__")}

    confApp["app_secret"] = "*****"
    confApp["db_password"] = '*****'

    res = {
        'environment': env_vars,
        'config': {'App': confApp}
    }
    return res
