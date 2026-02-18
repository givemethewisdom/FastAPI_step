import logging
import time
from datetime import datetime
from typing import Optional

from starlette import status

from DataBase.Shemas import TodooDB
from DataBase.repository.todoo_repository import TodooRepository
from DataBase.repository.user_repository import UserRepository
from app.exceptions import CustomException
from app.models.models_todoo import TodooResponse, Todoo

logger = logging.getLogger(__name__)


class TodooService:
    def __init__(self, todoo_repo: TodooRepository, user_repo: UserRepository):
        self.todoo_repo = todoo_repo
        self.user_repo = user_repo

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

        res = await self.todoo_repo.create_todo_repo(user_id, todoo_data)

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
