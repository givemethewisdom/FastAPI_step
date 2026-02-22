from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import UserCreate
from app.routing.user import create_user
from DataBase.Shemas import UserDB


"""def test_user_schema_validation():
    Тест только валидации Pydantic модели

    # Проверка без username
    with pytest.raises(ValidationError):
        UserCreate(password="password123", info="Без username")

    # Проверка без password
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", info="Без пароля")

    # Проверка с корректными данными
    user = UserCreate(username='some user', password="pass", info="ok")
    assert user.username == "some user"


@pytest.mark.asyncio
async def test_create_user_short():
    Создарние пользрователя
    # Arrange
    user_data = UserCreate(
        username="testuser",
        password="securepass",
        info="Test info"
    )

    #mock
    mock_session = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Act
    result = await create_user(user_data, mock_session)

    # Assert
    assert mock_session.add.called
    assert mock_session.commit.called
    assert mock_session.refresh.called

    # Проверяем что вернулся UserDB
    assert isinstance(result, UserDB)

    # Проверяем данные
    assert result.username == "testuser"
    assert result.password == "securepass"
    assert result.info == "Test info"""
