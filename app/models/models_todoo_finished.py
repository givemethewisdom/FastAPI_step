from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class Todoofinished(BaseModel):
    id: int
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
    user_id: int = Field(ge=1)
    created_at: datetime = Field(
        ...,
        description="вермя в формате ISO 8604(вроде бы XD)",
        example="2026-01-10T05:42:33.734734Z"
    )

    finished_at: datetime = Field(
        ...,
        description="вермя в формате ISO 8604(вроде бы XD)",
        example="2026-01-10T05:42:33.734734Z"
    )

    # пока не реализованно сокрее всего будет строкой
    # всего затрачено времени
    all_time_cost: int | None = None
