from pydantic import BaseModel


# Pydantic модель ответов на ошибки
class CustomExceptionModel(BaseModel):
    status_code: int
    er_message: str
    er_details: str


class CommonExceptionModel(BaseModel):
    status_code: int
    message: str
    error_code: str
