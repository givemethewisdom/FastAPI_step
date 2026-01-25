from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Базовый класс для моделей пользователя
class UserBase(BaseModel):
    username: str
    info: str | None = Field(None, max_length=30)
    model_config = ConfigDict(from_attributes=True)


# Модель для создания пользователя (входные данные)
class UserCreate(UserBase):
    """
    Модель для получения данных от клиента.
    В реальных проектах может содержать дополнительные поля,
    например, пароль, которые не возвращаются в ответе.
    """
    password: str = Field(min_length=1, max_length=128)


# Модель для возврата данных пользователя (выходные данные)
class UserReturn(UserBase):
    """
    Модель для сериализации данных пользователя.
    Включает технические поля из БД (id) и исключает чувствительные данные.
    """
    id: int  # ID всегда присфутствует после сохранения в БД
