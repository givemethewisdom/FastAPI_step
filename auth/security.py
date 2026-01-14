# security.py
import os
from datetime import UTC, datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi_limiter.depends import RateLimiter
from rbacx import Subject, Action, Resource, Context
from rbacx.adapters.fastapi import require_access
from starlette.requests import Request

from app.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 15


def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode.update({"type": 'access'})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode.update({"type": 'refresh'})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(token: str = Depends(oauth2_scheme), required_type: Optional[str] = None) -> str:
    """DI-обёртка под FastAPI (используем в dependencies.py)."""
    if required_type:
        return decode_token_with_type(token, required_type)
    return decode_token(token)


def decode_token(token: str) -> str:
    """Возвращает username из токена (клейм `sub`)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Неверный токен")
        return username

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен устарел")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Ошибка авторизации")


def decode_token_with_type(required_type: str, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if required_type:
            if payload.get("type") != required_type:
                raise HTTPException(401, detail="Wrong token type")
            return payload.get("sub")
        logger.warning('decode_token_with_type have no token type')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="не найден token type")

    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail="Expired token")

    except jwt.InvalidTokenError:
        raise HTTPException(401, detail="Invalid token")


def check_refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "refresh":
            raise HTTPException(401, detail="Wrong token type")

        if REFRESH_TOKEN_DB[username] != token:
            raise HTTPException(401, detail="token is not equal of stored token")

        return payload.get("sub")

    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail="Expired token")

    except jwt.InvalidTokenError:
        raise HTTPException(401, detail="Invalid token")


def username_from_request(request: Request) -> str:
    """Для rbacx: достаём Bearer-токен вручную и возвращаем subject.id."""
    auth = request.headers.get("Authorization", '')
    prefix = 'bearer '
    if not auth.lower().startswith(prefix):
        return 'anonymous'
    token = auth[len(prefix):].strip()

    try:
        return decode_token(token)
    except HTTPException:
        return 'anonymous'


def require_access_with_rate_limit(guard, resource: str, page: str):
    """проверка прав и выдача лимита запросов
    Пока нет(и скорее всего не будет)  у одного пользователя несколько ролей
    но ессли будут то роль выше в иерархии должна быть левее (индекс ноль)
    тут проверяется роль на первом месте
    """
    logger.info('если видно это сообщение то лимиты в require_access_with_rate_limit '
                'все еще тестовые')

    async def dependency(
            request: Request,
            response: Response,
            _=Depends(require_access(guard, make_env_builder(resource, page))),
    ):
        user = username_from_request(request)
        user_obj = get_user(user)
        role = getattr(user_obj, 'roles', 'common role')
        # для дебага маленькие значения
        if role[0] == 'admin':
            limiter = RateLimiter(times=10, seconds=10)
        elif role[0] == 'user':
            limiter = RateLimiter(times=5, seconds=10)
        elif role[0] == 'guest':
            limiter = RateLimiter(times=2, seconds=10)
        else:
            limiter = RateLimiter(times=1, seconds=10)

        await limiter(request,response)
        return user

    return dependency


# 2) Фабрика сборки окружения для rbacx
def make_env_builder(action_name: str, resource_type: str):
    """
    раньше вызывал в main в
    [Depends(require_access(guard, make_env_builder(action_name='view_user', resource_type='page')))])
    теперь буду в security в
    require_access_with_rate_limit
    """

    def build_env(request: Request):
        logger.info(f'env_builder start')
        username = username_from_request(request)
        user_obj = get_user(username)
        roles = user_obj.roles if user_obj else []
        subject = Subject(id=username, roles=roles)
        action = Action(action_name)
        resource = Resource(type=resource_type)
        context = Context()
        logger.info(f'env_builder end')
        return subject, action, resource, context

    return build_env
