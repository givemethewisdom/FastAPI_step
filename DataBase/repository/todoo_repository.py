import logging
from typing import List

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.Shemas import TodooDB
from DataBase.repository.base_repository import BaseRepository
from app.models.models_todoo import TodooResponse, Todoo, TodooComment

logger = logging.getLogger(__name__)


class TodooRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(TodooDB, db)

