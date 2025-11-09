# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


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
