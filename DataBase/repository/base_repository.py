"""модуль для однотипных запросов к разным ресурсам"""
import logging
from abc import ABC
from typing import TypeVar, Generic, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from DataBase.Shemas import UserDB, TodooFinishedDB
from app.exceptions import CustomException

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")


class BaseRepository(ABC, Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_obj_by_id(self, obj_id: int) -> type[ModelType] | None:
        """стандартный метод для всех get by id
        id как собственный id записи а не с join
        """
        try:
            res = await self.session.execute(
                select(self.model).where(self.model.id == obj_id)
            )

            ret_value = res.scalar_one_or_none()

            if not ret_value:
                return None

            return ret_value
        except Exception as e:
            logger.error(e)
            await self._handler_500(e, "get_obj_by_id")

    async def get_all(self, skip: int = 0, limit: int = 10) -> list[ModelType]:
        """стандартный метод для всех get all"""
        try:
            query = (select(self.model)
                     .offset(skip)
                     .limit(limit)
                     .order_by(self.model.id))

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
        logger.error('Error in %s.%s: %s', self.model.__name__, operation, e)
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='server error',
            message='try again later'
        )
