"""модуль для однотипных запросов к разным ресурсам"""

import logging
from abc import ABC
from typing import Generic, List, Optional, Sequence, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.exceptions import CustomException


logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")


class BaseRepository(ABC, Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_obj_by_id_base_repo(self, obj_id: int) -> type[ModelType] | None:
        """стандартный метод для всех get by id
        id как собственный id записи а не с join
        """
        try:
            # orm ДОЛЖЕН БЫТЬ БЫСТРЕЕ НО на такой выборке не понятно
            #
            return await self.session.get(self.model, obj_id)
        except Exception as e:
            logger.error(e)
            await self._handler_500(e, "get_obj_by_id")

    async def create_obj_base_repo(self, **kwargs) -> ModelType:
        """
        Универсальный метод создания записи
        user:
            username
            password
            info
            roles
        todoo:
            user_id
            title
            description
            comment
        """
        try:
            instance = self.model(**kwargs)
            self.session.add(instance)
            await self.session.flush()
            return instance

        except Exception as e:
            logger.error(e)
            await self._handler_500(e, "create")

    async def delete_obj_by_id_base_repo(self, obj_id: int) -> ModelType | None:
        """стандартный метод для всех delete by id (id записи а не с join)"""
        try:
            stmt = delete(self.model).where(self.model.id == obj_id).returning(self.model)

            res = await self.session.execute(stmt)
            obj = res.scalar_one_or_none()

            return obj

        except Exception as e:
            logger.error(e)
            await self._handler_500(e, "delete_obj_by_id")

    async def get_all_base_repo(self, skip: int, limit: int, filters: Optional[List] = None) -> list[ModelType]:
        """стандартный метод для всех get all"""
        try:
            query = select(self.model)

            if filters:
                query = query.where(*filters)

            query = query.offset(skip).limit(limit).order_by(self.model.id)

            result = await self.session.execute(query)

            # без этого return result.scalars().all() Expected type 'list[ModelType]',
            # got 'Sequence[Row | RowMapping
            # | Any]' instead
            items: Sequence[ModelType] = result.scalars().all()

            return list(items)
        except Exception as e:
            logger.error(e)
            await self._handler_500(e, "get_all")

    async def _handler_500(self, e: Exception, operation: str):
        logger.error("Error in %s.%s: %s", self.model.__name__, operation, e)
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server error",
            message="try again later",
        )
