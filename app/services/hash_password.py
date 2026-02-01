"""
Сервис хеширования и проверки хешированного пароля
"""

from passlib.context import CryptContext

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
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)



