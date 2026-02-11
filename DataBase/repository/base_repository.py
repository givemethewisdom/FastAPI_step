"""модуль для однотипных запросов к разным ресурсам"""
import logging

from sqlalchemy import select
from starlette import status

from DataBase.Shemas import UserDB, TodooFinishedDB
from app.exceptions import CustomException


logger = logging.getLogger(__name__)
logger.debug("This works in every module!")
class BaseDB:
    """базовый класс для всех get all"""

    def __init__(self, model, db):
        self.model = model
        self.db = db

    async def get_all(self, skip, limit):
        """шаблон запроса для всехз get user"""
        try:
            query = (select(self.model)
                     .offset(skip)
                     .limit(limit)
                     .order_by(self.model.id))
            result = await self.db.execute(query)

            return result.scalars().all()

        except Exception as e:
            logger.error('Error in %s %s', self.model.__name__, e)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='server error',
                message='try again later'
            )


class UserDBClass(BaseDB):
    def __init__(self, db):
        super().__init__(UserDB, db)


class TodooFinishedDBClass(BaseDB):
    def __init__(self, db):
        super().__init__(TodooFinishedDB, db)
