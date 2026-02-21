import logging
import time
from datetime import datetime, timezone
from typing import Optional

from starlette import status

from DataBase.Shemas import TodooDB
from DataBase.repository.finished_todoo_repo import FinishedTodooRepository
from DataBase.repository.todoo_repository import TodooRepository
from DataBase.repository.user_repository import UserRepository
from app.exceptions import CustomException
from app.models.models_todoo import TodooResponse, Todoo, TodooComment
from app.models.models_todoo_finished import Todoofinished

logger = logging.getLogger(__name__)


class TodooService:
    def __init__(self, todoo_repo: TodooRepository, user_repo: UserRepository, f_todoo_repo: FinishedTodooRepository):
        self.todoo_repo = todoo_repo
        self.user_repo = user_repo
        self.f_todoo_repo = f_todoo_repo

    async def create_todoo_serv(self, user_id: int, todoo_data: Todoo) -> TodooResponse:
        """создание задачи без проверки активности пользователя
        (флаг is_active для токена)
        """
        user = await self.user_repo.get_obj_by_id_base_repo(obj_id=user_id)

        if not user:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='user does not exist',
                message='make sure user exist'
            )

        res = await self.todoo_repo.create_obj_base_repo(
            user_id=user_id,
            title=todoo_data.title,
            description=todoo_data.description,
            comment=todoo_data.comment
        )

        try:
            await self.todoo_repo.session.commit()
            return res
        except Exception as e:
            logger.exception(e)
            await self.todoo_repo.session.rollback()

    async def get_all_todoo_serv(
            self,
            skip: int,
            limit: int,
            created_after: Optional[datetime],
            created_before: Optional[datetime]
    ):
        """get all todoo with date filter(optional)"""

        filters = []

        if created_after:
            filters.append(TodooDB.created_at >= created_after)

        if created_before:
            filters.append(TodooDB.created_at <= created_before)

        return await self.todoo_repo.get_all_base_repo(
            skip=skip,
            limit=limit,
            filters=filters
        )

    async def update_todoo_comment_serv(self, todoo_id: int, comment: TodooComment):
        """Update todoo info by id"""

        todoo = await self.todoo_repo.get_obj_by_id_base_repo(obj_id=todoo_id)

        if not todoo:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='todoo not found',
                message='make sure todoo exist'
            )

        todoo.comment = comment.comment
        try:
            await self.todoo_repo.session.commit()
            return todoo
        except Exception as e:
            await self.todoo_repo.session.rollback()
            logger.error(e)
            raise

    async def delete_todoo_by_id_serv(self, todoo_id: int) -> dict:
        """Delete todoo by id"""
        deleted_todo = await self.todoo_repo.delete_obj_by_id_base_repo(obj_id=todoo_id)
        if not deleted_todo:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='todoo not found',
                message='make sure todoo exist'
            )
        try:
            await self.todoo_repo.session.commit()
            return {'success': 'todoo deleted'}
        except Exception as e:
            await self.todoo_repo.session.rollback()
            logger.error(e)
            raise

    async def complete_todoo_serv(self, todoo_id: int) -> Todoofinished:
        """Complete todoo by id (delete from todoo add to comp-ed_todoo)"""
        cur_todoo = await self.todoo_repo.delete_obj_by_id_base_repo(todoo_id)

        if not cur_todoo:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='todoo not found',
                message='make sure todoo exist'
            )

        finished_at = datetime.now(timezone.utc)
        time_diff = finished_at - cur_todoo.created_at
        all_time_cost = int(time_diff.total_seconds())

        res = await self.f_todoo_repo.create_obj_base_repo(
            user_id=cur_todoo.user_id,
            title=cur_todoo.title,
            description=cur_todoo.description,
            comment=cur_todoo.comment,
            created_at=cur_todoo.created_at,
            finished_at=finished_at,
            all_time_cost=all_time_cost
        )

        try:
            await self.todoo_repo.session.commit()
            return res
        except Exception as e:
            await self.todoo_repo.session.rollback()
            logger.error(e)
            raise
