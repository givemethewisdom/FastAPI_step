from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Todoo(BaseModel):
    "модель для задачи без user id"

    title: str = Field(min_length=1, max_length=100, description="Заголовок задачи")
    description: str | None = Field(None, min_length=1, max_length=250, description="описание задачи")
    comment: str | None = Field(
        None, min_length=1, max_length=250, description="комментарий (меняется из @router.put('/{todoo_id}')"
    )


class TodooResponse(Todoo):
    """модель для овтета с id задачи датой и создания"""

    user_id: int = Field(ge=1)  #
    id: int  # возвращает бд с flush
    created_at: datetime = Field(
        ...,
        description="вермя в формате ISO 8604(вроде бы XD)",
        json_schema_extra={"example": "2026-01-10T05:42:33.734734Z"},
    )


class TodooComment(BaseModel):
    """модель для измениния только поля comment for todoo"""

    comment: str | None = Field(
        None, min_length=1, max_length=250, description="комментарий (меняется из @router.put('/{todoo_id}')"
    )
