# main.py
from fastapi import FastAPI
from pydantic import BaseModel

from app import config
from app.logger import logger

from .config import load_config


app = FastAPI()

config = load_config()

if config.debug:
    app.debug = True
else:
    app.debug = False
@app.get("/db")#логгирование
def get_db_info():
    logger.info(f"Connecting to database: {config.db.database_url}")
    return {"database_url": config.db.database_url}


class User(BaseModel):
    username: str
    message: str


@app.post("/")
async def root(user: User):
    """
    Здесь мы можем с переменной user, которая содержит объект класса User с соответствующими полями,
    выполнить любую логику – например, сохранить информацию в базу данных, передать в другую функцию и т.д.
    """
    print(f'Мы получили от юзера {user.username} такое сообщение: {user.message}')
    return user


@app.get("/c")
def read_root():
    logger.info("Handling request to root endpoint")
    return {"message": "Hello, World!"}
