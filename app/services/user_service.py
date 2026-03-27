"""用户服务，采用 Cache-Aside 模式。"""
import json
import random
import time
from typing import Optional

import redis.asyncio as redis
from tortoise.exceptions import IntegrityError

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import User

logger = log_util.get_logger("user_service")

NICKNAME_ADJECTIVES = [
    "Happy",
    "Swift",
    "Bright",
    "Cool",
    "Gentle",
    "Bold",
    "Calm",
    "Eager",
]
NICKNAME_NOUNS = [
    "User",
    "Traveler",
    "Explorer",
    "Dreamer",
    "Seeker",
    "Explorer",
    "Pioneer",
]
JOIN_LOCK_TIMEOUT_SECONDS = 10
JOIN_LOCK_BLOCKING_TIMEOUT_SECONDS = 3


class UserService:
    """用户服务类。"""

    @staticmethod
    async def _get_redis() -> redis.Redis:
        """获取 Redis 连接。"""
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @staticmethod
    def _generate_nickname() -> str:
        """生成随机昵称。"""
        adj = random.choice(NICKNAME_ADJECTIVES)
        noun = random.choice(NICKNAME_NOUNS)
        num = random.randint(100, 999)
        return f"{adj}{noun}{num}"

    @staticmethod
    def _generate_avatar() -> str:
        """生成随机头像。"""
        return f"{random.randint(1, 16)}.jpg"

    @classmethod
    async def allocate_userid(cls) -> int:
        """使用 Redis INCR 原子分配 userid。"""
        redis_client = await cls._get_redis()
        userid = await redis_client.incr(RedisKeys.USER_ID_SEQ)
        if userid < 10000000:
            await redis_client.set(RedisKeys.USER_ID_SEQ, 10000000)
            userid = 10000000
        return userid

    @classmethod
    async def get_user_cache(cls, deviceid: str) -> Optional[dict]:
        """从缓存读取用户信息。"""
        try:
            redis_client = await cls._get_redis()
            cache_key = RedisKeys.device_user_id(deviceid)
            cached = await redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit for deviceid: {deviceid}")
                return json.loads(cached)
            return None
        except Exception as exc:
            logger.warning(f"Redis get failed: {exc}")
            return None

    @classmethod
    async def set_user_cache(cls, user: User) -> None:
        """写入用户缓存。"""
        try:
            redis_client = await cls._get_redis()
            cache_key = RedisKeys.device_user_id(user.deviceid)
            user_data = await user.to_dict()
            await redis_client.setex(cache_key, 86400, json.dumps(user_data))
            logger.info(f"Cache set for deviceid: {user.deviceid}")
        except Exception as exc:
            logger.warning(f"Redis set failed: {exc}")

    @classmethod
    async def invalidate_user_cache(cls, deviceid: str) -> None:
        """删除用户缓存。"""
        try:
            redis_client = await cls._get_redis()
            cache_key = RedisKeys.device_user_id(deviceid)
            await redis_client.delete(cache_key)
            logger.info(f"Cache invalidated for deviceid: {deviceid}")
        except Exception as exc:
            logger.warning(f"Redis delete failed: {exc}")

    @classmethod
    async def _create_user_record(
            cls,
            clientid: str,
            deviceid: str,
            platform: Optional[int],
            nation: Optional[str],
            localLanguage: Optional[str],
            brand: Optional[str],
    ) -> User:
        """创建新用户记录。"""
        userid = await cls.allocate_userid()
        nick_name = cls._generate_nickname()
        avatar = cls._generate_avatar()
        user = await User.create(
            userid=userid,
            deviceid=deviceid,
            clientCode=clientid,
            platForm=platform if platform is not None else 0,
            nation=nation or "",
            localLanguage=localLanguage or "",
            brand=brand or "",
            nickName=nick_name,
            avartar=avatar,
            vip=0,
            time=int(time.time() * 1000),
        )
        logger.info(f"New user created: userid={userid}, deviceid={deviceid}")
        return user

    @classmethod
    async def _get_or_create_user(
            cls,
            clientid: str,
            deviceid: str,
            platform: Optional[int],
            nation: Optional[str],
            localLanguage: Optional[str],
            brand: Optional[str],
    ) -> tuple[User, bool]:
        """二次确认后查询或创建用户。"""
        user = await User.filter(deviceid=deviceid).first()
        if user:
            logger.info(f"DB hit after lock for deviceid: {deviceid}")
            return user, False

        try:
            user = await cls._create_user_record(
                clientid=clientid,
                deviceid=deviceid,
                platform=platform,
                nation=nation,
                localLanguage=localLanguage,
                brand=brand,
            )
            return user, True
        except IntegrityError as exc:
            logger.warning(
                f"Concurrent join fallback for deviceid={deviceid}: {exc}"
            )
            user = await User.filter(deviceid=deviceid).first()
            if not user:
                raise
            logger.info(
                "Existing user recovered after concurrent create: "
                f"userid={user.userid}, deviceid={deviceid}"
            )
            return user, False

    @classmethod
    async def _get_or_create_user_with_lock(
            cls,
            clientid: str,
            deviceid: str,
            platform: Optional[int],
            nation: Optional[str],
            localLanguage: Optional[str],
            brand: Optional[str],
    ) -> tuple[User, bool]:
        """使用 Redis 分布式锁串行化同一 deviceid 的创建。"""
        try:
            redis_client = await cls._get_redis()
        except Exception as exc:
            logger.warning(
                f"Join lock unavailable for deviceid={deviceid}, fallback without lock: {exc}"
            )
            return await cls._get_or_create_user(
                clientid=clientid,
                deviceid=deviceid,
                platform=platform,
                nation=nation,
                localLanguage=localLanguage,
                brand=brand,
            )

        lock = redis_client.lock(
            RedisKeys.join_device_lock(deviceid),
            timeout=JOIN_LOCK_TIMEOUT_SECONDS,
            blocking_timeout=JOIN_LOCK_BLOCKING_TIMEOUT_SECONDS,
        )
        acquired = False
        try:
            acquired = await lock.acquire()
            if not acquired:
                logger.warning(
                    f"Join lock acquire timeout for deviceid={deviceid}, fallback without lock"
                )
                return await cls._get_or_create_user(
                    clientid=clientid,
                    deviceid=deviceid,
                    platform=platform,
                    nation=nation,
                    localLanguage=localLanguage,
                    brand=brand,
                )

            logger.info(f"Join lock acquired for deviceid: {deviceid}")
            return await cls._get_or_create_user(
                clientid=clientid,
                deviceid=deviceid,
                platform=platform,
                nation=nation,
                localLanguage=localLanguage,
                brand=brand,
            )
        finally:
            if acquired:
                try:
                    await lock.release()
                except Exception as exc:
                    logger.warning(
                        f"Join lock release failed for deviceid={deviceid}: {exc}"
                    )

    @classmethod
    async def join(
            cls,
            clientid: str,
            deviceid: str,
            platform: Optional[int],
            nation: Optional[str],
            localLanguage: Optional[str],
            brand: Optional[str],
    ) -> dict:
        """处理用户注册/登录。"""
        cached = await cls.get_user_cache(deviceid)
        if cached:
            return cached

        user = await User.filter(deviceid=deviceid).first()
        created = False
        if user:
            logger.info(f"DB hit for deviceid: {deviceid}")
        else:
            user, created = await cls._get_or_create_user_with_lock(
                clientid=clientid,
                deviceid=deviceid,
                platform=platform,
                nation=nation,
                localLanguage=localLanguage,
                brand=brand,
            )

        if not created:
            logger.info(f"Existing user login: userid={user.userid}, deviceid={deviceid}")

        await cls.set_user_cache(user)

        # 初始化 vip 为 0
        vip_info = {"vip": 0}
        return await user.to_dict() | vip_info
