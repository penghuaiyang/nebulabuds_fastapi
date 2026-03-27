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
USER_CACHE_TTL_SECONDS = 86400


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
    async def _get_user_cache(cls, cache_key: str, cache_label: str) -> Optional[dict]:
        """从 Redis 读取用户缓存。"""
        try:
            redis_client = await cls._get_redis()
            cached = await redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit for {cache_label}")
                return json.loads(cached)
            return None
        except Exception as exc:
            logger.warning(f"Redis get failed for {cache_label}: {exc}")
            return None

    @classmethod
    async def get_user_cache(cls, deviceid: str) -> Optional[dict]:
        """按 deviceid 读取用户缓存。"""
        return await cls._get_user_cache(
            RedisKeys.device_user_id(deviceid),
            f"deviceid={deviceid}",
        )

    @classmethod
    async def get_user_cache_by_userid(cls, userid: int) -> Optional[dict]:
        """按 userid 读取用户缓存。"""
        return await cls._get_user_cache(
            RedisKeys.user_profile(userid),
            f"userid={userid}",
        )

    @classmethod
    async def set_user_cache(
            cls,
            user: User,
            user_data: Optional[dict] = None,
    ) -> None:
        """同时写入 deviceid 和 userid 两份用户缓存。"""
        try:
            redis_client = await cls._get_redis()
            user_data = user_data or await user.to_dict()
            payload = json.dumps(user_data)
            await redis_client.setex(
                RedisKeys.device_user_id(user.deviceid),
                USER_CACHE_TTL_SECONDS,
                payload,
            )
            await redis_client.setex(
                RedisKeys.user_profile(user.userid),
                USER_CACHE_TTL_SECONDS,
                payload,
            )
            logger.info(
                f"Cache set for deviceid={user.deviceid}, userid={user.userid}"
            )
        except Exception as exc:
            logger.warning(f"Redis set failed: {exc}")

    @classmethod
    async def invalidate_user_cache(
            cls,
            deviceid: Optional[str] = None,
            userid: Optional[int] = None,
    ) -> None:
        """按 deviceid 和 userid 删除用户缓存。"""
        keys = []
        if deviceid:
            keys.append(RedisKeys.device_user_id(deviceid))
        if userid is not None:
            keys.append(RedisKeys.user_profile(userid))
        if not keys:
            return

        try:
            redis_client = await cls._get_redis()
            await redis_client.delete(*keys)
            logger.info(
                "Cache invalidated for "
                f"deviceid={deviceid}, userid={userid}"
            )
        except Exception as exc:
            logger.warning(f"Redis delete failed: {exc}")

    @classmethod
    async def _query_user_by_userid(cls, userid: int) -> Optional[User]:
        """从数据库按 userid 读取用户。"""
        user = await User.filter(userid=userid).first()
        if user:
            logger.info(f"DB hit for userid: {userid}")
        return user

    @classmethod
    async def get_user_by_userid(cls, userid: int) -> Optional[dict]:
        """按 userid 读取用户信息，优先走缓存。"""
        cached = await cls.get_user_cache_by_userid(userid)
        if cached:
            return cached

        user = await cls._query_user_by_userid(userid)
        if not user:
            return None

        user_data = await user.to_dict()
        await cls.set_user_cache(user, user_data)
        return user_data

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
        vip_info = {"vip": 0}
        if cached:
            return cached | vip_info

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
        return await user.to_dict() | vip_info
