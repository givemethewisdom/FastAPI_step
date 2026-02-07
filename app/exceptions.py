from enum import Enum
from typing import Optional, Dict

from fastapi import HTTPException

from app.logger import logger


class CustomException(HTTPException):
    def __init__(self, detail: str, status_code: int, message: str):
        logger.debug('заглушка для кастом ексепшена из app/Exceptions')
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


class ErrorCode(str, Enum):
    """Стандартные коды ошибок приложения"""
    # Общие ошибки
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    FORBIDDEN = "FORBIDDEN"
    UNAUTHORIZED = "UNAUTHORIZED"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # Бизнес-ошибки
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    USER_EXISTS = "USER_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TODO_NOT_FOUND = "TODO_NOT_FOUND"
    TODO_ALREADY_COMPLETED = "TODO_ALREADY_COMPLETED"


class CommonException(HTTPException):
    """
    Кастомное исключение для CommonExceptionModel.
    Сохраняет status_code, message и error_code.
    """

    def __init__(
            self,
            status_code: int,
            message: str,
            error_code: Optional[str] = None,
            detail: Optional[str] = None,
            headers : Optional[Dict[str, str]] = None
    ):
        # detail для HTTPException, message для нашей модели
        super().__init__(
            status_code=status_code,
            detail=detail or message,  # detail должно быть строкой
            headers=headers
        )
        self.message = message
        self.error_code = error_code or self._default_error_code(status_code)
        self.headers = headers

    @staticmethod
    def _default_error_code(status_code: int) -> str:
        """Генерирует error_code на основе status_code"""
        error_codes = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            409: ErrorCode.USER_EXISTS,
            422: ErrorCode.VALIDATION_ERROR,
            500: ErrorCode.INTERNAL_ERROR,
        }
        return error_codes.get(status_code, "UNKNOWN_ERROR")
