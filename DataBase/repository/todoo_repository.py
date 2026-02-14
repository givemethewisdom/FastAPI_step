from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.Shemas import TodooDB
from DataBase.repository.base_repository import BaseRepository


class TodooRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(TodooDB, db)