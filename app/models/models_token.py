from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RefreshTokenResponse(BaseModel):
    "модель возвращаемых данных для refresh токена"
    token_id: int
    user_id: int
    username:str
    refresh_token: str
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)