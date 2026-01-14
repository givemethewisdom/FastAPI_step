from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Todoo(BaseModel):
    "модель для задачи без user id"
    title: str = Field(
        min_length=1,
        max_length=100,
        description="Заголовок задачи"
    )
    description: str | None = Field(
        None,
        min_length=1,
        max_length=250,
        description="описание задачи"
    )


class TodooUserId(Todoo):
    """модель для создания и обновления со всеми данными задачи кроме id
       Id инкементируется в DB
    """
    user_id: int = Field(ge=1)


class TodooResponse(TodooUserId):
    """модель для овтета с id задачи датой создания и
    all_time_cost : str | None = None - всего затрачено времени
    work_time_cost : str | None = None - затрачено рабочего времени
    """
    id:int
    created_at : datetime = Field(
        ...,
        description="вермя в формате ISO 8604(вроде бы XD)",
        example="2026-01-10T05:42:33.734734Z"
    )
