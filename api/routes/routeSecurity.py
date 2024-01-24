from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from api.models.modalUsers import UserDB
# from inlogform import InLogForm
# from api.core.dependencies import get_authorization_token
from api.core.database import db
from api.core.security import authenticate_user, SECRET_KEY, ALGORITHM, revok
import jwt

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = {"username": "johndoe", "email": "johndoe@example.com",
                 "full_name": "John Doe", "hashed_password": "hashed_password"}
    user = User(**user_dict)
    if form_data.username == user.username and form_data.password == user.hashed_password:
        return {"access_token": oauth2_scheme.create_token(user.username)}
    else:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")


@router.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    user = UserDB(**{"username": "johndoe", "email": "johndoe@example.com",
                     "full_name": "John Doe", "hashed_password": "hashed_password"})
    if token == oauth2_scheme.create_token(user.username):
        return {"message": "Hello, John Doe!"}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")


# Create a FastAPI route for login
@router.post("/login2")
async def login(username: str, password: str):
    # Verify the credentials using the `authenticate_user` function
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate a JSON Web Token (JWT) using the `jwt` library
    access_token = jwt.encode(
        {"sub": user.id}, SECRET_KEY, algorithm=ALGORITHM)

    # Return the access token as a response
    return {"access_token": access_token}

# Create a FastAPI route for logout


@router.post("/logout")
async def logout():
    # Get the current user from the request context
    user = await get_current_user()

    # Revoke the user's access token
    await revoke_access_token(user.id)

    # Return a success message
    return {"message": "Successfully logged out"}
