from typing import List

from fastapi import HTTPException, status
from functools import wraps

"""
Это декоратор для доступа на основе ролей. Он тут чисто в учебных целях т.к. лучше делать на основе депенденси
(я вообще забыл что он тут есть)
"""
class PermissionChecker:
    '''Декоратор для првоерки ролей пользователя'''

    def __init__(self, roles: List[str]):
        self.roles = roles  # список разрешенных ролей

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')  # поулччаем текущего польхователя
            if not user:
                raise HTTPException(status_code=403, detail='Required authentication')

            if 'admin' in user.roles:
                return await func(*args, **kwargs)

            if not any(role in user.roles for role in self.roles):
                raise HTTPException(
                    status_code=403,
                    detail='недостаточно прав для доступа'
                )
            return await func(*args, **kwargs)
        return wrapper
