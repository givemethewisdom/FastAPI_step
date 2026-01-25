
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Async PostgreSQL URL (ВАЖНО: postgresql+asyncpg://)
POSTGRES_URL = os.getenv("POSTGRES_URL")


# Async engine
engine = create_async_engine(
    POSTGRES_URL,
    echo=True,  # SQL логи (False в production)
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base для моделей
Base = declarative_base()

# Dependency для получения сессии
async def get_async_session() -> AsyncSession:
    """
    Dependency для получения async сессии SQLAlchemy.
    сам закрывает сессию
    Использовать: session: AsyncSession = Depends(get_async_session)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()