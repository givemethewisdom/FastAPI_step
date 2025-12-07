import re
from typing import Optional

from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field, field_validator

from app.config import domens


class User(BaseModel):
    username: str = Field(..., min_length=1, max_length=15)
    password: str = Field(..., min_length=1, max_length=10)
