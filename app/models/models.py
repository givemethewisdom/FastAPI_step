from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.services.hash_password import PasswordService


# Базовый класс для моделей пользователя
class UserBase(BaseModel):
    username: str


# Модель для создания пользователя (входные данные)
class UserPass(UserBase):
    "модель для Log In и база для create new suer"

    password: str = Field(min_length=3, max_length=128)

    #@field_validator('password')
    #def validate_password(cls, password):
        #if len(password) < 3:
            #raise ValueError('Password must be at least 3 characters')
        #return PasswordService.hash_password(password)


class UserCreate(UserPass):
    "модель для создания нового юзера"
    info: str | None = Field(None, max_length=30)
    model_config = ConfigDict(from_attributes=True)


# Модель для возврата данных пользователя (выходные данные)
class UserReturn(BaseModel):
    """
    Модель для сериализации данных пользователя.
    Включает технические поля из БД (id) и исключает чувствительные данные.
    """
    username: str
    info: str | None = Field(None, max_length=30)
    id: int  # ID всегда присфутствует после сохранения в БД
    roles: str


class UserTokenResponse(UserReturn):
    access_token: str
    refresh_token: str
