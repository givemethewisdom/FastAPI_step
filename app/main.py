import os
from contextlib import asynccontextmanager
from pathlib import Path

from databases import Database
from dotenv import load_dotenv
from fastapi import FastAPI

from DataBase.Database import Base, engine
from .config import load_config
# Импорт роутеров
from .routing import user, todoo

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
POSTGRES_URL = os.getenv("POSTGRES_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

config = load_config()

database = Database(POSTGRES_URL)



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

if config.debug:
    app.debug = True
else:
    app.debug = False

# Импорт роутеров

app.include_router(user.router)
app.include_router(todoo.router)
