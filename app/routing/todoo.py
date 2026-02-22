import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from rbacx.adapters.fastapi import require_access

from app.models.models_todoo import Todoo, TodooComment, TodooResponse
from app.models.models_todoo_finished import Todoofinished
from app.services.dependencies import TodooServiceDep
from auth.guard import guard
from auth.security import make_env_builder


router = APIRouter(prefix="/todoo", tags=["todoo"])

logger = logging.getLogger(__name__)


# для отладки доступ по user
@router.post("/{user_id}/create", response_model=TodooResponse)
async def create_todoo(user_id: int, todoo_data: Todoo, todoo_service: TodooServiceDep):
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
    return await todoo_service.create_todoo_serv(user_id=user_id, todoo_data=todoo_data)


@router.get("/get_all", response_model=List[TodooResponse])
async def get_all_todoo(
    todoo_service: TodooServiceDep,
    skip: int = 0,
    limit: int = 10,
    created_after: Optional[datetime] = Query(
        None, description="Созданные ПОСЛЕ", json_schema_extra={"example": "2026-01-01T00:00:00"}
    ),
    created_before: Optional[datetime] = Query(
        None, description="Созданные ДО)", json_schema_extra={"example": "2026-01-01T00:00:00"}
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
    return await todoo_service.get_all_todoo_serv(skip, limit, created_after, created_before)


@router.patch("/{todoo_id}", response_model=TodooResponse)
async def update_todoo_comment(todoo_id: int, comment: TodooComment, todoo_service: TodooServiceDep):
    """
    обновление комментария к задаче(со стороны проверяющего к исполнителю)
    по сути может поменять любой admin для любого(admin,user)
    т.к. нет конкретных кураторов для пользователей(не интересно реализовывать)

    Параметры:
    - todoo_id: ID задачи в базе данных
    - comment: комментрий

    Возвращает:
    - Обновленные данные о задаче в формате TodooResponse
    - 404 ошибку если задача не найдена
    - 500 ошибку при проблемах с базой данных
    """
    return await todoo_service.update_todoo_comment_serv(todoo_id, comment)


@router.delete("/{todoo_id}", response_model=dict)
async def delete_todoo(todoo_id: int, todoo_service: TodooServiceDep):
    """
    Удаление todoo из базы данных по ID.

    Параметры:
    - todoo_id: id для удаления

    Возвращает:
    - Сообщение об успешном удалении
    - 404 ошибку если запись не найдена
    - 500 ошибку при проблемах с базой данных
    """
    return await todoo_service.delete_todoo_by_id_serv(todoo_id)


@router.post("/complete_todoo/{todoo_id}", response_model=Todoofinished)
async def complete_todoo(todoo_id: int, todoo_service: TodooServiceDep):
    """
    Атомарное завершение todoo с переходом в TodooFinished.

    Параметры:
    - todoo_id: идентификатор записи

    Возвращает:
    - Json переброшенных данных
    - 404 ошибку если запись не найдена
    - 500 ошибку при проблемах с базой данных
    """
    return await todoo_service.complete_todoo_serv(todoo_id)
