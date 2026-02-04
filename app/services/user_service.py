from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from DataBase.repository import check_user_exists, create_new_user
from app.models.models import UserCreate, UserTokenResponse
from auth.security import create_access_token, create_refresh_token


class UserService:
    def __init__(self):
        pass

    async def create_user_with_tokens(self, user_data: UserCreate, db: AsyncSession) -> UserTokenResponse:
        """
        Полный цикл создания пользователя с токенами.
        """
        if await check_user_exists(user_data.username, db):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь c таким именем уже существует"
            )

        db_user = await create_new_user(user_data, db)

        access_token = create_access_token({'sub': db_user.username})
        refresh_token = create_refresh_token({'sub': db_user.username})

        return UserTokenResponse(
            id=db_user.id,
            username=db_user.username,
            info=db_user.info,
            access_token=access_token,
            refresh_token=refresh_token
        )
