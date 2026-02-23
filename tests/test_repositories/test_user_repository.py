from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.models import UserCreate, UserTokenResponse
from app.services.token_service import TokenService
from app.services.user_service import UserService
from DataBase.repository.user_repository import UserRepository


@pytest.mark.asyncio
class TestUserRepository:
    async def test_get_user_with_token_by_name_found(self, mock_session, mock_db_user):
        """комменты пока не выучу"""
        # === НАСТРОЙКА МОКОВ ===

        # Создаём имитацию результата запроса
        mock_result = MagicMock()  # ← имитирует то, что вернёт execute()

        # Настраиваем синхронный метод scalar_one_or_none
        mock_result.scalar_one_or_none.return_value = mock_db_user  # ← вернёт нашего пользователя

        # Настраиваем асинхронный метод execute
        mock_session.execute.return_value = mock_result  # ← execute() вернёт mock_result

        # === ВЫПОЛНЕНИЕ ===
        repo = UserRepository(mock_session)
        result = await repo.get_user_with_token_by_name_repo("testuser")

        # === ПРОВЕРКИ ===
        assert result == mock_db_user
        mock_session.execute.assert_called_once()

        # Проверяем, что использовался joinedload
        call_args = mock_session.execute.call_args[0][0]
        assert "left outer join" in str(call_args).lower()  # алхимия конвертирует joinedload в left outer join

    async def test_get_user_with_token_by_name_not_found(self, mock_session):
        """Тест: пользователь не найден"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # ← Просто return_value
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_user_with_token_by_name_repo("some username")

        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_with_tokens_success(mock_session):
        """Тест успешного создания пользователя с токенами"""
        # 1. Подготовка моков
        mock_user_repo = AsyncMock()
        mock_token_repo = AsyncMock()
        mock_token_service = TokenService(mock_token_repo)

        mock_user_repo.get_user_with_token_by_name_repo = AsyncMock(return_value=None)

        mock_db_user = MagicMock()
        mock_db_user.id = 1
        mock_db_user.username = "testuser"
        mock_db_user.info = "some info"
        mock_db_user.roles = "user"
        mock_user_repo.create_obj_base_repo = AsyncMock(return_value=mock_db_user)
        mock_token_service.save_refresh_token_in_db_service = AsyncMock()

        user_service = UserService(user_repo=mock_user_repo, token_service=mock_token_service)

        user_data = UserCreate(username="testuser", password="TestPass123!", info="some info")

        # ВАЖНО мокать все внещние зависимости!!
        with (
            patch("app.services.user_service.PasswordService.hash_password") as mock_hash,
            patch("app.services.user_service.create_access_token") as mock_access,
            patch("app.services.user_service.create_refresh_token") as mock_refresh,
        ):
            mock_hash.return_value = "hashed_password_123"
            mock_access.return_value = "mock_access_token"
            mock_refresh.return_value = "mock_refresh_token"

            result = await user_service.create_user_with_tokens_service(user_data, role="user")

            mock_hash.assert_called_once_with("TestPass123!")

            mock_user_repo.create_obj_base_repo.assert_called_once_with(
                username="testuser",
                password="hashed_password_123",
                info="some info",
                roles="user",
            )

            mock_access.assert_called_once_with({"sub": "testuser", "uid": 1})
            mock_refresh.assert_called_once_with({"sub": "testuser", "uid": 1})

            mock_token_service.save_refresh_token_in_db_service.assert_called_once_with(
                user_id=1, token="mock_refresh_token"
            )

            mock_user_repo.session.commit.assert_called_once()

            assert result.id == 1
            assert result.username == "testuser"
            assert result.info == "some info"
            assert result.roles == "user"
            assert result.access_token == "mock_access_token"
            assert result.refresh_token == "mock_refresh_token"

    async def test_create_new_user_with_special_chars(self, mock_session):
        """Тест: создание пользователя со спецсимволами"""

        repo = UserRepository(mock_session)
        result = await repo.create_obj_base_repo(username="@ad12", password="Zx!/*", info="None", roles="user")

        assert result.username == "@ad12"
        assert result.roles == "user"
        assert result.info == "None"

    async def test_create_new_user_empty_info(self, mock_session):
        """Тест: создание пользователя без info"""

        repo = UserRepository(mock_session)
        result = await repo.create_obj_base_repo(
            username="@ad12",
            password="Zx!/*",
            # info="None",
            roles="user",
        )

        assert result.username == "@ad12"
        assert result.info is None
