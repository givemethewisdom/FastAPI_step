import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from isort import settings
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from DataBase.Database import get_async_session
from DataBase.Shemas import TodooDB, UserDB, TodooFinishedDB
from app import config
from app.config import get_config
from app.exception_handlers import custom_exception_handler
from app.exceptions import CustomException, CommonException, ErrorCode

from app.models.models_todoo import Todoo, TodooUserId, TodooResponse
from app.models.models_todoo_finished import Todoofinished

# config = get_config()

router = APIRouter(
    prefix="/todoo",
    tags=["todoo"]
)

logger = logging.getLogger(__name__)


@router.post("/create", response_model=TodooResponse)
async def create_todoo(
        todoo: TodooUserId,
        session: AsyncSession = Depends(get_async_session)
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

    try:
        user = await session.get(UserDB, todoo.user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="user is not exist")

        # Создаем объект БД
        db_todoo = TodooDB(**todoo.dict())

        session.add(db_todoo)
        await session.commit()
        await session.refresh(db_todoo)
        return db_todoo

    # пробрасываем сгенерированынй експепшен выше чтобы его не перехватывал except Exception as e:
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'ошибка добавления задачи {str(e)}'
        )


@router.get("/get_all", response_model=List[TodooResponse])
async def get_all_todoo(
        skip: int = 0,
        limit: int = 10,
        created_after: Optional[datetime] = Query(
            None,
            description="Созданные ПОСЛЕ",
            #Pydantic V2.0
            json_schema_extra={
                'example':'2026-01-01T00:00:00'
            }

        ),
        created_before: Optional[datetime] = Query(
            None,
            description="Созданные ДО)",
            json_schema_extra={
                'example':'2026-01-01T00:00:00'
            }
        ),

        session: AsyncSession = Depends(get_async_session)
):
    """
    Получение информации обо всех задачах.

    Параметры:
    - skip - смещение
    - limit - Кол-во задач

    Возвращает:
    - Данные о задаче в формате TodooResponse
    - пустой список если нет задач
    """
    try:
        stmt = select(TodooDB)

        filter = []

        if created_after:
            filter.append(TodooDB.created_at >= created_after)

        if created_before:
            filter.append(TodooDB.created_at <= created_before)

        if filter:
            stmt = stmt.where(*filter)

        stmt = stmt.order_by(TodooDB.id).offset(skip).limit(limit)
        query = await session.execute(stmt)
        todos = query.scalars().all()
        return todos

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'ошибка поулчаения задач {str(e)}'
        )


@router.put('/{todoo_id}', response_model=TodooResponse)
async def update_todoo(
        todoo_id: int,
        todoo: TodooUserId,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Полное обновление данных о задаче по ID.
    Колгда будет доступ по правам это только для админа

    Параметры:
    - todoo_id: ID задачи в базе данных
    - todoo: новые данные задачи

    Возвращает:
    - Обновленные данные о задаче в формате TodooResponse
    - 404 ошибку если задача не найдена
    - 500 ошибку при проблемах с базой данных

Пример запроса:
{
  "title": "string",
  "description": "string",
  "user_id": 1
}
    """
    try:
        user_stmt = await session.get(
            UserDB,
            todoo.user_id
        )

        todoo_data = todoo.model_dump(exclude_unset=True)

        if not user_stmt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {todoo.user_id} not found"
            )

        query = (
            update(TodooDB)
            .where(TodooDB.id == todoo_id)
            .values(**todoo_data)
            .returning(TodooDB)
        )
        result = await session.execute(query)
        new_todoo_data = result.scalar_one_or_none()

        if not new_todoo_data:
            raise CommonException(
                status_code=status.HTTP_404_NOT_FOUND,
                message='Invalid Input'
            )

        await session.commit()
        return new_todoo_data

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'ошибка добавления данных о пользователе {str(e)}'
        )


@router.delete("/{todoo_id}", response_model=dict)
async def delete_todoo(
        todoo_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Удаление todoo из базы данных по ID.

    Параметры:
    - todoo_id: идентификатор записи для удаления

    Возвращает:
    - Сообщение об успешном удалении
    - 404 ошибку если запись не найдена
    - 500 ошибку при проблемах с базой данных
    """
    try:
        stmt = (delete(TodooDB)
                .where(TodooDB.id == todoo_id))

        result = await session.execute(stmt)

        if not result.rowcount:
            raise HTTPException(
                status_code=404,
                detail="Запись с указаным id не найдена"
            )

        await session.commit()
        return {'todoo deleted with id': todoo_id}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления пользователя: {str(e)}"
        )


@router.post("/complet_todoo/{todoo_id}", response_model=Todoofinished)
async def complete_todoo(
        todoo_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Атомарное завершение todoo с переходом в TodooFinished.

    Параметры:
    - todoo_id: идентификатор записи

    Возвращает:
    - Json переброшенных данных
    - 404 ошибку если запись не найдена
    - 500 ошибку при проблемах с базой данных
    """
    try:
        # Начало транзакции
        async with session.begin():
            # Блокировка строки защита от race condition(не уверен что это нужно)
            todoo = await session.get(TodooDB, todoo_id, with_for_update=True)

            if not todoo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Todoo not found"
                )

            finished_at = datetime.now(timezone.utc)
            time_diff = finished_at - todoo.created_at
            all_time_cost = int(time_diff.total_seconds())

            # Создаем завершенную задачу
            todoo_data = TodooFinishedDB(
                user_id=todoo.user_id,
                title=todoo.title,
                description=todoo.description,
                created_at=todoo.created_at,
                finished_at=finished_at,
                all_time_cost=all_time_cost
            )

            # Добавляем и удаляем в одной транзакции
            session.add(todoo_data)
            await session.delete(todoo)

            # Коммит произойдет автоматически при выходе из with
            # Если ошибка - автоматический rollback

        # Обновляем данные после успешного коммита
        await session.refresh(todoo_data)
        return todoo_data

    except HTTPException:
        # Перебрасываем HTTP исключения
        raise
    except Exception as e:
        # Все остальные ошибки
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при завершении задачи: {str(e)}'
        )


@router.get("/get_all_finished", response_model=List[Todoofinished])
async def get_all_todoo(
        skip: int = 0,
        limit: int = 10,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Получение информации обо всех закочненных задачах.

    Параметры:
    - skip - смещение
    - limit - Кол-во задач

    Возвращает:
    - Данные о задаче в формате List[Todoofinished]
    - пустой список если нет задач
    """
    try:
        query = await session.execute(
            select(TodooFinishedDB)
            .offset(skip)
            .limit(limit)
            .order_by(TodooFinishedDB.id)
        )

        todoos = query.scalars().all()

        return todoos

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'ошибка получения задач {str(e)}'
        )


@router.get("/analytics", response_model=dict)
async def get_analitics(session: AsyncSession = Depends(get_async_session)):
    """
    Метод для получения аналитики по задачам
    """
    try:
        # 1. Количество активных задач
        active_count = await session.scalar(select(func.count(TodooDB.id))) or 0

        # 2. Количество завершенных задач
        completed_count = await session.scalar(select(func.count(TodooFinishedDB.id))) or 0

        # 3. Общее время завершенных задач
        total_time_result = await session.execute(
            select(func.coalesce(func.sum(TodooFinishedDB.all_time_cost), 0))
        )
        total_time = total_time_result.scalar() or 0

        all_tasks = active_count + completed_count

        # Среднее время
        avg_time = total_time / completed_count if completed_count > 0 else 0

        return {
            'all_tasks': all_tasks,
            'completed': completed_count,
            'in_progress': active_count,
            'total_time_on_complete': total_time,  # отдаю в секундах (фронт пересчитает как хочет)
            'total_time_hours': total_time / 3600,  # в часах даже лишнее(наверное)
            'avg_time_on_complete': avg_time,
            'avg_time_on_complete_hours': avg_time / 3600 if avg_time > 0 else 0,
            'completion_rate': f"{(completed_count / all_tasks * 100):.1f}%" if all_tasks > 0 else "0%"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{todoo_id}", response_model=TodooResponse)
async def get_todoo(
        todoo_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Получение информации о задаче по  ID.

    Параметры:
    - todoo_id: идентификатор задачи в БД

    Возвращает:
    - Данные задаче в формате TodooResponse
    - 404 ошибку если задача не найдена
    """
    try:
        todoo = await session.get(TodooDB, todoo_id)
        if not todoo:
            if config.debug:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Costum exception todoo not found',
                    message='u r atemp to (pohyi)'
                )
            else:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Costum exception todoo not found',
                    message='awdawdawd'
                )

        return todoo

    except HTTPException:
        raise
    except Exception as e:
        logger.error('Error getting todo ?', todoo_id)

        if config.debug:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'ошибка получения задачи {str(e)}'
            )
        else:
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'CustomException code 500 for router get /todoo_id',
                message='Упс.. кто-то что-то где-то сломал'
            )

