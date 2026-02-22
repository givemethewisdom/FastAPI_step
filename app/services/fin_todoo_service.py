import logging
from datetime import datetime
from typing import Optional

from DataBase.Shemas import TodooFinishedDB
from DataBase.repository.finished_todoo_repo import FinishedTodooRepository
from DataBase.repository.todoo_repository import TodooRepository

logger = logging.getLogger(__name__)


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

    async def get_analytics_serv(self):
        """get analytics"""
        active_count = len(await self.todoo_repo.get_all_base_repo(skip=0, limit=9999999))

        if active_count == 0:
            active_count = 0

        completed_count = len(await self.f_todoo_repo.get_all_base_repo(skip=0, limit=9999999))

        if completed_count == 0:
            completed_count = 0

        total_time = await self.f_todoo_repo.total_time_result_repo()

        all_tasks = active_count + completed_count

        avg_time = total_time / completed_count if completed_count > 0 else 0
        logger.debug(avg_time)

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
