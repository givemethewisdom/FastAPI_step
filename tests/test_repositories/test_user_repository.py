from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.sql import Select

from app.models.models import UserCreate
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

    @patch("DataBase.repository.user_repository.PasswordService")
    async def test_create_new_user_success(self, mock_password_service, mock_session):
        """Тест: успешное создание пользователя"""
        mock_password_service.hash_password.return_value = "hashed_pass"

        user_data = UserCreate(username="testuser", password="testpass!", info="some info")

        repo = UserRepository(mock_session)
        result = await repo.create_new_user_repo(user_data, role="user")

        assert result.username == "testuser"
        assert result.password == "hashed_pass"
        assert result.roles == "user"
        assert result.info == "some info"
        mock_session.add.assert_called_once_with(result)

    async def test_create_new_user_with_special_chars(self, mock_session):
        """Тест: создание пользователя со спецсимволами"""
        user_data = UserCreate(username="user@#123", password="pass123", info="special info")

        repo = UserRepository(mock_session)
        result = await repo.create_new_user_repo(user_data, role="admin")

        assert result.username == "user@#123"
        assert result.roles == "admin"
        assert result.info == "special info"

    async def test_create_new_user_empty_info(self, mock_session):
        """Тест: создание пользователя без info"""
        user_data = UserCreate(
            username="testuser",
            password="pass123",
            # info не указано
        )

        repo = UserRepository(mock_session)
        result = await repo.create_new_user_repo(user_data, role="user")

        assert result.username == "testuser"
        assert result.info is None
