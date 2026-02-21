import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from databases import Database
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from jwt import ExpiredSignatureError
from rbacx import Guard, HotReloader
from rbacx.store import FilePolicySource

from DataBase.Database import Base, engine
from app import logger
from app.exception_handlers import custom_exception_handler, global_exception_handler, validation_exception_handler, \
    common_exception_handler, jwt_exceptions_expired_signature_error_hendler
from app.exceptions import CustomException, CommonException
from app.logger import setup_logger
from app.routing import user, todoo, fin_todoo
from auth.guard import guard

env_path = Path(__file__).parent.parent / '.env'
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
    # 1. Создаем таблицы (асинхронно)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
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
