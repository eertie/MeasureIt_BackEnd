from fastapi import Depends
from api.core.config import AppConfig
import secrets

secret = secrets.token_urlsafe(20)

#  Dependency functions for routes in FastAPI


def get_authorization_token():
    print(secret)
    return secret
