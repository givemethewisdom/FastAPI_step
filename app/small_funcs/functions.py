import hashlib
import secrets
import sys

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext



security = HTTPBasic()

# по этой схеме работает/ некоторые другие нет
hashed_content = CryptContext(
    schemes=["sha256_crypt"],
    deprecated="auto"
)


async def hash_password(password: str) -> str:
    """
    Создает хеш пароля при регистрации
    """
    return hashed_content.hash(password)


async def verify_password(plain_password: str,
                          hashed_password: str) -> bool:
    """
    Сравнения введеного пароля с хешем в БД
    """
    if not hashed_content.verify(plain_password, hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return hashed_content.verify(plain_password, hashed_password)


async def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username is None or credentials.password is None:
        raise HTTPException(401,
                            detail='Incorrect credentials',
                            headers={'WWW-Authenticate': "Basic"})

    if credentials.username not in fake_db:
        raise HTTPException(401,
                            detail='Incorrect credentials',
                            headers={'WWW-Authenticate': "Basic"})

    if not hashed_content.verify(credentials.password, fake_db[credentials.username]):
        raise HTTPException(401,
                            detail='Incorrect credentials',
                            headers={'WWW-Authenticate': "Basic"})

    return credentials.username


