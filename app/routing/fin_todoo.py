import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from app.models.models_todoo_finished import Todoofinished
from app.services.dependencies import FinTodooServiceDep


router = APIRouter(prefix="/finished_todoo", tags=["fin_todoo"])

logger = logging.getLogger(__name__)


@router.get("/analytics", response_model=dict)
async def get_analytics(fin_todoo_service: FinTodooServiceDep):
    """
    Метод для получения аналитики по задачам
    """
    return await fin_todoo_service.get_analytics_serv()


@router.get("/get_all", response_model=List[Todoofinished])
async def get_all_todoo(
    fin_todoo_service: FinTodooServiceDep,
    skip: int = 0,
    limit: int = 10,
    created_after: Optional[datetime] = Query(
        None,
        description="Созданные ПОСЛЕ",
        json_schema_extra={"example": "2026-01-01T00:00:00"},
    ),
    finished_before: Optional[datetime] = Query(
        None,
        description="Созданные ДО)",
        json_schema_extra={"example": "2027-01-01T00:00:00"},
    ),
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
    return await fin_todoo_service.get_all_fin_todoo_serv(skip, limit, created_after, finished_before)
