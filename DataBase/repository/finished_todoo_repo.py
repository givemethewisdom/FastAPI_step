import logging

from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.Shemas import TodooFinishedDB
from DataBase.repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class FinishedTodooRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(TodooFinishedDB, db)

