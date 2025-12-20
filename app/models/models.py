import re
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field, field_validator


from app.config import domens


class UserOnlyName(BaseModel):
    username: str = Field(..., min_length=1, max_length=15)


class User(UserOnlyName):
    password: str = Field(..., min_length=1, max_length=10)


class UserBaseFields(UserOnlyName):
    '''просто модель юзера с базовыми полями'''
    full_name: str = Field(..., min_length=1, max_length=15)
    email: str = Field(..., min_length=10, max_length=20)
    disabled: bool = Field(default=False, description="idk")
    roles: List[str] = Field(..., description="list of user roles")


class UserLogin(BaseModel):
    """модель для входа в систему"""
    username: str = Field(..., min_length=1, max_length=10)
    password: str = Field(..., min_length=0, max_length=10)

