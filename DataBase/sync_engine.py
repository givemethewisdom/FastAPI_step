"""
создание синхронного движка для RBAC
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

from sqlalchemy.testing.pickleable import User

from DataBase.Shemas import UserDB

# Синхронный URL (заменяем asyncpg на psycopg2)
POSTGRES_URL_SYNC = os.getenv("POSTGRES_URL").replace("+asyncpg", "+psycopg2")

sync_engine = create_engine(POSTGRES_URL_SYNC, echo=True)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def get_sync_db() -> Session:
    """Синхронная сессия для использования в rbacx"""
    db = SyncSessionLocal()
    try:
        return db
    finally:
        db.close()


# Упрощенная синхронная версия get_user
def get_user_sync(username: str) -> User | None:
    """Синхронная версия получения пользователя для rbacx"""
    from sqlalchemy import select

    db = get_sync_db()
    try:
        result = db.execute(
            select(UserDB).where(UserDB.username == username)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        roles_str = db_user.roles or "user"
        if "," in roles_str:
            roles_list = [role.strip() for role in roles_str.split(",")]
        else:
            roles_list = [roles_str.strip()] if roles_str.strip() else ["user"]

        return User(
            username=db_user.username,
            roles=roles_list,
            full_name=db_user.info,
            email=None,
            disabled=False
        )
    finally:
        db.close()

