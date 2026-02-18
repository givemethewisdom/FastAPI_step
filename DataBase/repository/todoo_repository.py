from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.Shemas import TodooDB
from DataBase.repository.base_repository import BaseRepository
from app.models.models_todoo import TodooResponse, Todoo


class TodooRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(TodooDB, db)

    async def create_todo_repo(self, user_id: int, todoo_data: Todoo) -> TodooResponse:
        db_todoo = TodooDB(
            user_id=user_id,
            title=todoo_data.title,
            description=todoo_data.description
            )

        self.session.add(db_todoo)
        await self.session.flush()
        return db_todoo


