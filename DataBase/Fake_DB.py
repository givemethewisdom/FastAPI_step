from hashlib import sha256

from fastapi import FastAPI


fake_db = {}  # empty for future temp users

USERS_DATA = [
    {"username": "admin", "password": "adminpass"}  # В реальной базе данных пароли должны храниться в виде хэшей
]

REFRESH_TOKEN_DB = {

}


def get_user(username: str) -> dict | None:
    """
    Функция для поиска пользователя по имени пользователя.
    В реальном проекте это должно быть запросом к базе данных.
    """
    for user in USERS_DATA:
        if user.get("username") == username:
            return user
    return None

