import logging
import time

import jwt
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jwt import ExpiredSignatureError

from app.exceptions import CommonException, CustomException
from app.models.exception_models import CommonExceptionModel, CustomExceptionModel


logger = logging.getLogger(__name__)
logger.debug("This works in every module!")


async def custom_exception_handler(request: Request, exc: CustomException):
    "обработчик ошибок пока только в get todoo by id"
    error = jsonable_encoder(
        CustomExceptionModel(status_code=exc.status_code, er_message=exc.message, er_details=exc.detail)
    )
    return JSONResponse(status_code=exc.status_code, content=error)


async def global_exception_handler(request: Request, exc: Exception):
    "глобальный обработчик ошибок"
    "он ловит все неучтенные ошибки но я не понимаю как))"
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error (from global_exception_handler)"},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("validation_exception_handler")
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


async def jwt_exceptions_expired_signature_error_hendler(request: Request, exc: ExpiredSignatureError):
    "хендлер для expired acces token exception"
    return JSONResponse(status_code=401, content={"token_error": "Expired signature"})


async def common_exception_handler(request: Request, exc: CommonException):
    print("common_exception_handler")
    "обработчик для свамых частых случаев"
    start_time = time.perf_counter()

    error = jsonable_encoder(
        CommonExceptionModel(status_code=exc.status_code, message=exc.message, error_code=exc.error_code)
    )

    end_time = time.perf_counter()
    spend_time = str((end_time - start_time) * 1000)  # милисек

    response_headers = exc.headers or {}
    response_headers["X-ErrorHandleTime"] = spend_time
    return JSONResponse(status_code=exc.status_code, content=error, headers=response_headers)
