from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import jwt
from passlib.context import CryptContext
from api.core.config import AppConfig
from api.models.modalUsers import UserDB, read_user


# todo maybe: CREATE TABLE AccessToken (
#   id INT NOT NULL AUTO_INCREMENT,
#   user_id INT NOT NULL,
#   token VARCHAR(255) NOT NULL,
#   expires_at TIMESTAMP NOT NULL,
#   PRIMARY KEY (id),
#   UNIQUE KEY (token)
# );

security = HTTPBasic()
SECRET_KEY = AppConfig.app_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Define a dependency that will be used to retrieve the current user
async def get_current_user():
    # Get the access token from the request headers
    authorization = Request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=401, detail="Missing Authorization header")

    # Extract the access token from the authorization header
    access_token = authorization.split(" ")[1]

    # Decode the access token using the `jwt` library
    decoded_token = jwt.decode(
        access_token, SECRET_KEY, algorithms=[ALGORITHM])

    # Retrieve the user ID from the decoded token
    user_id = decoded_token["sub"]

    # Return the user object
    return await read_user(user_id)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db, username: str, password: str):
    user = await read_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Define a function that will be used to revoke the user's access token


# def delete_access_token(access_token):
#     # Delete the access token from the tokens table
#     db.session.query(Token).filter_by(access_token=access_token).delete()
#     db.session.commit()


# async def revoke_access_token(user_id):
#     # Revoke the access token by removing it from the database
#     await delete_access_token(user_id)
