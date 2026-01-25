
from httpx import AsyncClient, ASGITransport

from DataBase.Database import Base, get_async_session
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app

# Тестовая БД в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    # Создаем движок для тестовой БД
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,  # Включите для отладки SQL запросов
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )

    # Сначала удаляем ВСЕ таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Создаем ВСЕ таблицы (включая связанные)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Удаляем таблицы после теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    # Создаем сессию для тестов
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session):
    # Переопределяем зависимость get_async_session

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_async_session] = override_get_db

    # Используем ASGITransport для тестирования FastAPI приложения
    async with AsyncClient(
        transport=ASGITransport(app=app),  #создание клиента
        base_url="http://test"
    ) as ac:
        yield ac

    # Очищаем переопределение
    app.dependency_overrides.clear()



