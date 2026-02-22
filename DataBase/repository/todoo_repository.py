import logging

from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.repository.base_repository import BaseRepository
from DataBase.Shemas import TodooDB


logger = logging.getLogger(__name__)


class TodooRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(TodooDB, db)
