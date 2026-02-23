import logging
import os
from unittest.mock import AsyncMock, MagicMock

import pytest


os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test_secret_key")
os.environ.setdefault("REFRESH_SECRET", "test_refresh_secret")

# Теперь импортируем приложение - игнорируем E402 для следующих строк
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.models.models import UserCreate, UserTokenResponse  # noqa: E402
from app.services.token_service import TokenService  # noqa: E402
from DataBase.repository.token_repository import TokenRepository  # noqa: E402
from DataBase.repository.user_repository import UserRepository  # noqa: E402


# Тестовая БД в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

logger = logging.getLogger(__name__)

"""@pytest_asyncio.fixture(scope="function")
async def test_engine():
    Движок для тестовой БД SQLite с поддержкой Foreign Keys
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False
        }
    )

    # Включаем Foreign Keys для SQLite
    async with engine.connect() as conn:
        await conn.execute(text("PRAGMA foreign_keys = ON"))
        await conn.commit()

    # Сначала удаляем ВСЕ таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Создаем ВСЕ таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Проверяем что таблицы создались
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = result.fetchall()
        logger.info('table created'.format(tables))

    yield engine

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
            transport=ASGITransport(app=app),  # создание клиента
            base_url="http://test"
    ) as ac:
        yield ac

    # Очищаем переопределение
    app.dependency_overrides.clear()"""


@pytest.fixture
def mock_session():
    """Мок сессии БД"""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_user_repo(mock_session):
    """Мок репозитория пользователей"""
    repo = AsyncMock(spec=UserRepository)
    repo.session = mock_session
    repo.get_user_with_token_by_name = AsyncMock()
    repo.create_new_user = AsyncMock()
    return repo


@pytest.fixture
def mock_token_repo(mock_session):
    """Мок репозитория токенов"""
    repo = AsyncMock(spec=TokenRepository)
    repo.session = mock_session
    repo.save_refresh_token = AsyncMock()
    repo.get_active_token = AsyncMock()
    repo.delete_token = AsyncMock()
    return repo


@pytest.fixture
def mock_token_service(mock_token_repo):
    """Мок сервиса токенов"""
    service = AsyncMock(spec=TokenService)
    service.save_refresh_token_in_db_service = AsyncMock()
    service.hash_token_service = MagicMock(return_value="hashed_token")
    return service


@pytest.fixture
def user_create_data():
    """Тестовые данные для создания пользователя"""
    return UserCreate(username="testuser", password="testpass!", info="bio")


@pytest.fixture
def mock_db_user():
    """Мок пользователя из БД"""
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.info = "bio"
    user.roles = "user"
    return user


@pytest.fixture
def user_token_response():
    """Пример ответа с токенами"""
    return UserTokenResponse(
        id=1,
        roles="user",
        username="testuser",
        info="bio",
        access_token="access_token",
        refresh_token="refresh_token",
    )
