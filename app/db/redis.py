from typing import AsyncIterator, Optional

import redis.asyncio as redis

from app.core.config import settings
from app.common.utils.log_utils import log_util

logger = log_util.get_logger("redis")

redis_pool: Optional[redis.ConnectionPool] = None


async def init_redis_pool() -> redis.ConnectionPool:
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool.from_url(
            settings.redis_dsn,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            health_check_interval=30,
        )

        # Ensure the connection is healthy when the app starts
        client = redis.Redis(connection_pool=redis_pool)
        await client.ping()
        logger.info("Redis connection pool initialized")

    return redis_pool


async def close_redis_pool() -> None:
    global redis_pool
    if redis_pool is not None:
        await redis_pool.disconnect()
        redis_pool = None
        logger.info("Redis connection pool closed")


async def get_redis() -> AsyncIterator[redis.Redis]:
    if redis_pool is None:
        await init_redis_pool()

    client = redis.Redis(connection_pool=redis_pool)
    yield client


async def get_redis_client() -> Optional[redis.Redis]:
    """Return a Redis client from the shared pool without requiring a context manager."""

    if redis_pool is None:
        await init_redis_pool()

    if redis_pool is None:
        return None

    return redis.Redis(connection_pool=redis_pool)
