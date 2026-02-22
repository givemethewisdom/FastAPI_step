import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.repository.base_repository import BaseRepository
from DataBase.Shemas import TodooFinishedDB


logger = logging.getLogger(__name__)


class FinishedTodooRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(TodooFinishedDB, db)

    async def total_time_result_repo(self):
        try:

            total_time_result = await self.session.execute(
                select(func.coalesce(func.sum(TodooFinishedDB.all_time_cost), 0))
            )
            return total_time_result.scalar() or 0

        except Exception as e:
            logger.error(e)
            await self._handler_500(e, "total_time_result_repo")
