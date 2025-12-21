import os
from contextlib import asynccontextmanager
from pathlib import Path

import redis.asyncio as redis
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi_limiter.depends import RateLimiter

from DataBase.DB import get_user, USERS_DATA, REFRESH_TOKEN_DB, USERS_FOR_DELETE
from auth.dependencies import get_current_user
from auth.guard import guard, init_guard
from auth.rbac import PermissionChecker

from .config import load_config
from .logger import logger
from .models.models import User, UserBaseFields, UserLogin, UserOnlyName
from auth.security import get_user_from_token, create_access_token, create_refresh_token, check_refresh_token, \
    username_from_request, require_access_with_rate_limit
from .small_funcs.functions import hash_password, verify_password

from rbacx import Subject, Action, Resource, Context
from rbacx.adapters.fastapi import require_access

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

SECRET_KEY = os.getenv("SECRET_KEY")





@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения.
    Инициализирует и закрывает соединения.
    это для кастомного рейт лимитера на основе ролей
    """
    # Запуск - инициализация Redis и Limiter
    global redis_connection
    init_guard()

    try:
        # Подключение к Redis
        redis_connection = redis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )

        # Инициализация лимитера
        await FastAPILimiter.init(redis_connection)
        logger.info("Rate limiter initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize rate limiter: {e}")
        redis_connection = None

    yield

    # Завершение - закрытие соединений
    if redis_connection:
        await redis_connection.close()
        logger.info("Redis connection closed")


app = FastAPI(lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

config = load_config()

if config.debug:
    app.debug = True
else:
    app.debug = False


@app.post('/register')
@limiter.limit("10/minute")
async def register(request: Request, user: User):
    if get_user(user.username):
        logger.warning(f"User {user.username} lrdy exist")
        raise HTTPException(status_code=409, detail='User already exists!')

    hash_pass = await hash_password(user.password)

    USERS_DATA.append({'username': user.username,
                       'password': hash_pass})

    logger.info(f"user {user.username} added in dict")

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={'message': 'new user created'})


@app.post("/login")
async def login(request: Request, user_in: UserLogin):
    """ маршрут аутентификации"""
    for user in USERS_DATA:
        if user['username'] == user_in.username and user['password'] == user_in.password:
            token = create_access_token({'sub': user_in.username})
            return {'access_token': token, 'token_type': 'bearer'}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid u4etnie dannie')


@app.get("/protected_resource")
async def protected_resource(current_user: UserBaseFields = Depends(get_current_user)):
    return {"Access granted to protected resource for user, and admin"}


@app.post('/refresh')
async def refresh(request: Request, username: str = Depends(check_refresh_token)):
    """
    Функция принимает refresh token as token а возвращает 'sub' то есть username
    """
    access_token = create_access_token({"sub": username})
    refresh_token = create_refresh_token({"sub": username})
    logger.info(f"user grant {username} new refresh token ")
    REFRESH_TOKEN_DB[username] = refresh_token
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.get("/admin")
@PermissionChecker(['admin'])
async def admin_info(request: Request, current_user: UserBaseFields = Depends(get_current_user)):
    """Маршрут для администраторов"""
    return {"message": f"Hello, {current_user.username}! Welcome to the admin page."}


@app.get("/user", dependencies=[
    Depends(require_access_with_rate_limit(guard, 'view_user', 'page'))
])
async def user_info(request: Request, current_user: User = Depends(get_current_user)):

    """Маршрут для пользователей"""
    return {"message": f"Hello, {current_user.username}! Welcome to the user page."}


@app.get("/about_me")
@limiter.limit("3/minute")
async def about_me(request: Request, current_user: User = Depends(get_current_user)):
    """Информация о текущем пользователе"""
    return current_user


@app.delete("/delete_res")
async def delete_res(user: UserOnlyName):
    del USERS_FOR_DELETE[user.username]
    logger.info(f'user {user.username} successfully deleted')
    return {f"user {user.username} deleted"}


@app.post("/add_res")
async def add_res(user: UserLogin):
    # не хочу делать нормальную модель т.к. это все скоро переделаю под ДБ
    USERS_FOR_DELETE[user.username] = user.password
    logger.info(f'user {user.username} successfully add his info')
    return {f"info added"}

