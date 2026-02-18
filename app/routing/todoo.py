import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from app.models.models_todoo import Todoo, TodooResponse
from app.services import todoo_service
from app.services.dependencies import TokenServiceDep, TodooServiceDep
from app.services.todoo_service import TodooService

router = APIRouter(
    prefix="/todoo",
    tags=["todoo"]
)

logger = logging.getLogger(__name__)


@router.post("/{user_id}/create", response_model=TodooResponse)
async def create_todoo(
        user_id: int,
        todoo_data: Todoo,
        todoo_service: TodooServiceDep
):
    """
    Создание новой задачи.
    Возвращает:
    - TodooResponse с данными созданной задачи и ее ID из БД
    Пример тела запроса:
    {
        "title": "string",
        "description": "string",
        "completed": false,
        "user_id": 1
    }
    """
    return await todoo_service.create_todoo_serv(
        user_id=user_id,
        todoo_data=todoo_data
    )

#надо ограничить доступ но для отладки пока без этого
@router.get("/get_all", response_model=List[TodooResponse])
async def get_all_todoo(
        todoo_service: TodooServiceDep,
        skip: int = 0,
        limit: int = 10,
        created_after: Optional[datetime] = Query(
            None,
            description="Созданные ПОСЛЕ",
            # Pydantic V2.0
            json_schema_extra={
                'example': '2026-01-01T00:00:00'
            }

        ),
        created_before: Optional[datetime] = Query(
            None,
            description="Созданные ДО)",
            json_schema_extra={
                'example': '2026-01-01T00:00:00'
            }
        )
):
    """
    Получение информации обо всех не завершенных задачах.

    Параметры:
    - skip - смещение
    - limit - Кол-во задач
    Возвращает:
    - Данные о задачах в формате TodooResponse
    - пустой список если нет задач
    """
    return await todoo_service.get_all_todoo_serv(
        skip,
        limit,
        created_after,
        created_before
    )
