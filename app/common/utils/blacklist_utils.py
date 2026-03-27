"""黑名单工具"""
import os
import time
from typing import FrozenSet, Tuple

from app.db.redis import get_redis_client
from app.common.utils.log_utils import log_util

logger = log_util.get_logger("blacklist")

BLACKLIST_CACHE_TTL_SECONDS = int(os.getenv("BLACKLIST_CACHE_TTL_SECONDS", "60"))
_blacklist_cache: Tuple[FrozenSet[str], FrozenSet[str], float] = (
    frozenset(),
    frozenset(),
    0.0,
)
_blacklist_lock = False


async def _load_blacklist_sets() -> Tuple[FrozenSet[str], FrozenSet[str]]:
    """从 Redis 加载用户和设备黑名单集合"""
    client = await get_redis_client()
    if client is None:
        logger.error("Redis client not available")
        return frozenset(), frozenset()

    try:
        user_ids = set(await client.smembers("NEW_BLACK_USERID"))
        device_ids = set(await client.smembers("NEW_BLACK_DEVICEID"))
        return frozenset(user_ids), frozenset(device_ids)
    except Exception as e:
        logger.error(f"Failed to load blacklist: {e}")
        return frozenset(), frozenset()


async def get_blacklist_sets() -> Tuple[FrozenSet[str], FrozenSet[str]]:
    """获取带短时缓存的黑名单集合"""
    global _blacklist_cache, _blacklist_lock

    user_ids, device_ids, expires_at = _blacklist_cache
    now = time.monotonic()
    if expires_at > now:
        return user_ids, device_ids

    if not _blacklist_lock:
        _blacklist_lock = True
        try:
            user_ids, device_ids = await _load_blacklist_sets()
            _blacklist_cache = (
                user_ids,
                device_ids,
                now + BLACKLIST_CACHE_TTL_SECONDS,
            )
        finally:
            _blacklist_lock = False

    return _blacklist_cache[0], _blacklist_cache[1]


async def is_blacklisted(userid: int | str, deviceid: str) -> bool:
    """判断当前用户或设备是否命中黑名单"""
    user_ids, device_ids = await get_blacklist_sets()
    return str(userid) in user_ids or deviceid in device_ids
