import os
from contextlib import asynccontextmanager
from pathlib import Path

from databases import Database
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from jwt import ExpiredSignatureError

from app.exception_handlers import (
    common_exception_handler,
    custom_exception_handler,
    global_exception_handler,
    jwt_exceptions_expired_signature_error_hendler,
    validation_exception_handler,
)
from app.exceptions import CommonException, CustomException
from app.logger import setup_logger
from app.routing import fin_todoo, todoo, user
from DataBase.Database import Base, engine


env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)
POSTGRES_URL = os.getenv("POSTGRES_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

database = Database(POSTGRES_URL)

setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async lifespan для SQLAlchemy.
    """
    # 1. Создаем таблицы (асинхронно) это при старте
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 2 это при остановке
    await engine.dispose()


app = FastAPI(
    title="FastAPI + Async SQLAlchemy",
    description="Async SQLAlchemy example",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)  # все еще работает не так как я предпологаю
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(CommonException, common_exception_handler)
app.add_exception_handler(ExpiredSignatureError, jwt_exceptions_expired_signature_error_hendler)

# Импорт роутеров
app.include_router(user.router)
app.include_router(todoo.router)
app.include_router(fin_todoo.router)
