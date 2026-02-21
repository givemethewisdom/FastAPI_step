from datetime import datetime, timedelta
from typing import Type
from unittest.mock import patch, MagicMock

import pytest

from DataBase.Shemas import TokenDB
from DataBase.repository.token_repository import TokenRepository
from DataBase.repository.user_repository import UserRepository
from app.models.models import UserCreate


@pytest.mark.asyncio
class TestTokenRepository:

    @pytest.mark.asyncio
    async def test_save_refresh_token_success(self, mock_session):
        expires_at = datetime.now() + timedelta(minutes=10_000)

        repo = TokenRepository(mock_session)
        result = await repo.save_refresh_token(
            user_id=1,
            token_hash='hashed_token',
            expire_at=expires_at
        )

        # Проверка поведения
        mock_session.execute.assert_called_once()
        mock_session.add.assert_called_once()
        await mock_session.flush()

        # Проверка переданных значений
        assert result.user_id == 1
        assert result.refresh_token == 'hashed_token'
        assert result.expires_at == expires_at

        # Проверка значений по умолчанию
        assert hasattr(result, 'is_active')

        # Проверка наличия полей (не конкретных значений)
        assert hasattr(result, 'id')
        assert hasattr(result, 'created_at')

    async def test_get_refresh_token_found(self, mock_session):
        """Тест: токен найден по user_id"""
        # Создаём тестовый токен
        expected_token = TokenDB(
            id=1,
            user_id=1,
            refresh_token="hashed_token_123",
            expires_at=datetime.now(),
            is_active=True
        )

        # Настраиваем мок для результата запроса
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_token
        mock_session.execute.return_value = mock_result

        repo = TokenRepository(mock_session)
        result = await repo.get_refresh_by_user_id(user_id=1)

        # Проверки
        assert result == expected_token
        assert result.user_id == 1
        assert result.refresh_token == "hashed_token_123"

        # Проверяем, что execute был вызван
        mock_session.execute.assert_called_once()

    async def test_get_refresh_token_not_found(self, mock_session):
        """Тест: токен не найден"""
        # Настраиваем мок, что токена нет
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = TokenRepository(mock_session)
        result = await repo.get_refresh_by_user_id(user_id=999)

        # Проверки
        assert result is None
        mock_session.execute.assert_called_once()
