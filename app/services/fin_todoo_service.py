from datetime import datetime
from typing import Optional

from DataBase.Shemas import TodooFinishedDB
from DataBase.repository.finished_todoo_repo import FinishedTodooRepository
from DataBase.repository.todoo_repository import TodooRepository


class FinTodooService:
    def __init__(self, todoo_repo: TodooRepository, f_todoo_repo: FinishedTodooRepository):
        self.todoo_repo = todoo_repo
        self.f_todoo_repo = f_todoo_repo

    async def get_all_fin_todoo_serv(
            self,
            skip: int,
            limit: int,
            created_after: Optional[datetime],
            finished_before: Optional[datetime]
    ):
        """get all todoo with date filter(optional)"""

        filters = []

        if created_after:
            filters.append(TodooFinishedDB.created_at >= created_after)

        if finished_before:
            filters.append(TodooFinishedDB.finished_at <= finished_before)

        return await self.f_todoo_repo.get_all_base_repo(
            skip=skip,
            limit=limit,
            filters=filters
        )
