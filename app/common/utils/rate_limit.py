import inspect
from functools import wraps
from typing import Callable, Optional

from fastapi import Request

from app.common.base.base_reponse import api_write
from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client

logger = log_util.get_logger("rate_limit")


def _extract_request(args, kwargs) -> Optional[Request]:
    for arg in args:
        if isinstance(arg, Request):
            return arg
    for value in kwargs.values():
        if isinstance(value, Request):
            return value
    return None


def _default_identifier(request: Request) -> str:
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"

    device_id = request.headers.get("X-Device-ID")
    if device_id:
        return f"device:{device_id}"

    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


def rate_limit(
        limit: int,
        window_seconds: int,
        *,
        identifier_func: Optional[Callable[[Request], str]] = None,
        prefix: str = "ratelimit",
):
    if limit <= 0 or window_seconds <= 0:
        raise ValueError("limit and window_seconds must be positive integers")

    def decorator(func: Callable):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("rate_limit decorator only supports async endpoints")

        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = _extract_request(args, kwargs)
            if request is None:
                logger.warning("rate_limit skipped: Request not found in args/kwargs")
                return await func(*args, **kwargs)

            identity = identifier_func(request) if identifier_func else None
            if not identity:
                identity = _default_identifier(request)
            endpoint_id = request.url.path
            key = f"{prefix}:{endpoint_id}:{identity}"
            print(key)

            client = await get_redis_client()
            if client is None:
                logger.warning("rate_limit skipped: Redis unavailable")
                return await func(*args, **kwargs)

            try:
                count = await client.incr(key)
                if count == 1:
                    await client.expire(key, window_seconds)

                if count > limit:
                    ttl = await client.ttl(key)
                    retry_after = ttl if ttl is not None and ttl >= 0 else window_seconds
                    return await api_write(
                        code=-29,
                        message="请求过于频繁",
                        data={"retry_after": retry_after},
                        request=request,
                    )
            except Exception as exc:
                logger.warning(f"rate_limit failed open due to Redis error: {exc}")
                return await func(*args, **kwargs)

            return await func(*args, **kwargs)

        return wrapper

    return decorator
