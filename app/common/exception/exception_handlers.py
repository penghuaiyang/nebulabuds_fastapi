import traceback
from typing import Union

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError, OperationalError
from redis.exceptions import RedisError

from app.common.exception.exceptions import BaseAPIException, AuthenticationException
from app.common import api_write
from app.common import log_util

exception_logger = log_util.get_logger("exception")


async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    exception_logger.warning(
        f"API异常: {exc.message} | 路径: {request.url.path} | 方法: {request.method} | 详情: {exc.details}"
    )
    return await api_write(
        code=exc.code,
        message=exc.message,
        message_language=exc.message_language,
        data=exc.details,
        request=request,
    )


async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]):
    exception_logger.warning(
        f"HTTP异常: {exc.detail} | 状态码: {exc.status_code} | 路径: {request.url.path} | 方法: {request.method}"
    )

    status_messages = {
        400: "请求参数错误",
        401: "未授权访问",
        403: "禁止访问",
        404: "请求的资源不存在",
        405: "请求方法不允许",
        422: "请求参数验证失败",
        429: "请求过于频繁",
        500: "服务器内部错误",
        502: "网关错误",
        503: "服务不可用"
    }

    message = status_messages.get(exc.status_code, "未知错误")

    return await api_write(
        code=exc.status_code,
        message=message,
        data={"detail": str(exc.detail)},
        request=request,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exception_logger.warning(
        f"参数验证异常: {exc.errors()} | 路径: {request.url.path} | 方法: {request.method}"
    )

    error_details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # 跳过'body'
        error_details.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return await api_write(
        code=-24,
        message="请求参数验证失败",
        data={"errors": error_details},
        request=request,
    )


async def tortoise_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, DoesNotExist):
        exception_logger.warning(
            f"数据不存在: {str(exc)} | 路径: {request.url.path} | 方法: {request.method}"
        )
        return await api_write(
            code=-23,
            message="请求的数据不存在",
            data={"detail": str(exc)},
            request=request,
        )

    elif isinstance(exc, IntegrityError):
        exception_logger.error(
            f"数据完整性错误: {str(exc)} | 路径: {request.url.path} | 方法: {request.method}"
        )
        return await api_write(
            code=-26,
            message="数据完整性约束违反",
            data={"detail": "数据操作违反了完整性约束"},
            request=request,
        )

    elif isinstance(exc, OperationalError):
        exception_logger.error(
            f"数据库操作错误: {str(exc)} | 路径: {request.url.path} | 方法: {request.method}"
        )
        return await api_write(
            code=-26,
            message="数据库操作失败",
            data={"detail": "数据库连接或操作异常"},
            request=request,
        )

    exception_logger.error(
        f"数据库未知异常: {str(exc)} | 路径: {request.url.path} | 方法: {request.method}"
    )
    return await api_write(
        code=-26,
        message="数据库操作异常",
        data={"detail": "数据库操作发生未知错误"},
        request=request,
    )


async def redis_exception_handler(request: Request, exc: RedisError):
    exception_logger.error(
        f"Redis异常: {str(exc)} | 路径: {request.url.path} | 方法: {request.method}"
    )

    return await api_write(
        code=-26,
        message="缓存服务异常",
        data={"detail": "Redis连接或操作异常"},
        request=request,
    )


async def general_exception_handler(request: Request, exc: Exception):
    exception_logger.error(
        f"未捕获异常: {str(exc)} | 路径: {request.url.path} | 方法: {request.method} | "
        f"堆栈: {traceback.format_exc()}"
    )

    return await api_write(
        code=-1,
        message="服务器内部错误",
        data={"detail": "系统发生未知错误，请联系管理员"},
        request=request,
    )
