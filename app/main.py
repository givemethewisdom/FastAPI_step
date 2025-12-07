import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from DataBase.Fake_DB import fake_db, USERS_DATA, get_user
from .config import load_config
from .logger import logger
from .models.models import User
from .security import create_jwt_token, get_user_from_token
from .small_funcs.functions import hash_password, verify_password

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

SECRET_KEY = os.getenv("SECRET_KEY")

"""
Will it be in GIT?(cannot push this shiit)
"""

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

config = load_config()

if config.debug:
    app.debug = True
else:
    app.debug = False


@app.post('/register')
@limiter.limit("1/minute")
async def register(request: Request, user: User):

    if get_user(user.username):
        logger.warning(f"User {user.username} lrdy exist")
        raise HTTPException(status_code=409, detail='User already exists!')

    hash_pass = await hash_password(user.password)
    logger.info(f"pass 1 {hash_pass}")

    USERS_DATA.append({'username': user.username,
                       'password': hash_pass})

    logger.info(f"user {user.username} added in dict")

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={'message': 'new user created'}
    )


@app.post("/login")
@limiter.limit("5/minute", key_func=get_remote_address)
async def login(request: Request, user_in: User):
    current_user = get_user(user_in.username)

    if current_user:
        if await verify_password(user_in.password, current_user['password']):
            token = create_jwt_token({"sub": user_in.username})
            return {"access_token": token}

    raise HTTPException(status_code=401, detail='user not found')


@app.get("/protected_resource")
async def protected_resource(token: str = Depends(get_user_from_token)):
    user = get_user(token)
    logger.info(f"user: {user}")

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User is not exist"
        )

    return {"message": "Access granted to protected resource"}
