"""统一错误处理。"""

import logging
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    AppException,
    DuplicateException,
    ForbiddenException,
    NotFoundException,
    RateLimitException,
    ValidationException,
)

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """注册统一异常处理器。"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """处理应用自定义异常。 """
        # 记录日志
        logger.warning(f"AppException: {exc.code} - {exc.message}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        """处理资源未找到异常。 """
        # 不记录日志，避免日志泛滥
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(ForbiddenException)
    async def forbidden_handler(request: Request, exc: ForbiddenException):
        """处理权限不足异常。 """
        logger.warning(f"ForbiddenException: {exc.message}")

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(DuplicateException)
    async def duplicate_handler(request: Request, exc: DuplicateException):
        """处理重复资源异常。 """
        logger.info(f"DuplicateException: {exc.message}")

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(ValidationException)
    async def validation_handler(request: Request, exc: ValidationException):
        """处理验证失败异常。 """
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(RateLimitException)
    async def rate_limit_handler(request: Request, exc: RateLimitException):
        """处理速率限制异常。 """
        headers = {}
        if exc.retry_after:
            headers["Retry-After"] = str(exc.retry_after)

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": exc.message, "code": exc.code},
            headers=headers,
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """处理数据库完整性错误。 """
        # 记录详细错误到日志，但返回通用错误
        logger.error(f"Database integrity error: {str(exc)}")

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "数据操作冲突，请检查数据是否重复", "code": "INTEGRITY_ERROR"},
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError):
        """处理 Pydantic 验证错误。 """
        # 提取第一个错误信息
        errors = exc.errors()
        if errors:
            first_error = errors[0]
            field = ".".join(str(loc) for loc in first_error["loc"])
            message = f"{field}: {first_error['msg']}"
        else:
            message = "数据验证失败"

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": message, "code": "VALIDATION_ERROR"},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """处理未捕获的异常。 """
        # 记录详细错误到日志
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)

        # 返回通用错误，不泄露内部信息
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "服务器内部错误，请稍后重试", "code": "INTERNAL_ERROR"},
        )
