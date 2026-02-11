"""
Сервис хеширования и проверки хешированного пароля
"""
import passlib
from passlib.context import CryptContext
from starlette import status

from app.exceptions import CustomException


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,      # количество итераций
    argon2__memory_cost=1024, # использование памяти в KiB
    argon2__parallelism=2,    # количество параллельных потоков
)


class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """сравнение пароля с хешем пароля"""

        try:
            bool_res = pwd_context.verify(plain_password, hashed_password)
            if not bool_res:
                raise CustomException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Incorrect username or password',
                    message='на самом деле только pass но не палим перед брут форсом'
                )
            return pwd_context.verify(plain_password, hashed_password)

        except passlib.exc.UnknownHashError:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Incorrect username or password',
                message='это поле вообще просто атк придумал не знаю что сюда писать'
            )



