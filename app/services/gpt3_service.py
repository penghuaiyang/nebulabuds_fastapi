"""GPT3 AI 对话服务层."""
import time
from typing import Any

import redis.asyncio as redis

from app.common.utils.gpt4mini_utils import gpt41mini_agent
from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import Mac
from app.services.user_service import UserService

logger = log_util.get_logger("gpt3_service")

AI_DAY_LIMIT_NORMAL = 20
AI_DAY_LIMIT_VIP = 500
PVMB_CLIENT_ID = "PVMB8x1N"
AI_NUM_LIMIT_NORMAL = 50
MAC_BINDING_CACHE_TTL_SECONDS = 300
MAC_BINDING_NEGATIVE_CACHE_TTL_SECONDS = 60
AI_QUOTA_RESERVATION_TTL_SECONDS = 300

CLIENT_DB_START = {
    "tx-11033": 0,
    "tx-11055": 1,
    "tx-11069": 2,
    "tx-11105": 3,
    "tx-11106": 4,
    "tx-11154": 5,
    "tx-11175": 6,
    "tx-11212": 7,
    "tx-11479": 8,
    "tx-11522": 9,
    "tx-11558": 10,
    "tx-11607": 11,
    "tx-11624": 12,
    "tx-11725": 13,
    "tx-11743": 14,
    "tx-11766": 15,
    "tx-11791": 16,
    "tx-11863": 17,
    "tx-11914": 18,
    "tx-11929": 19,
    "tx-12030": 20,
    "tx-12043": 21,
    "tx-12299": 22,
    "tx-12305": 23,
    "tx-12332": 24,
    "tx-12351": 25,
    "tx-12410": 26,
    "tx-12425": 27,
    "tx-12433": 28,
    "tx-12434": 29,
}

RESERVE_AI_QUOTA_SCRIPT = """
local total_limit = tonumber(ARGV[1])
local day_limit = tonumber(ARGV[2])
local reserve_ttl = tonumber(ARGV[3])

local total_count = tonumber(redis.call('GET', KEYS[1]) or '0')
local day_count = tonumber(redis.call('GET', KEYS[2]) or '0')
local total_pending = tonumber(redis.call('GET', KEYS[3]) or '0')
local day_pending = tonumber(redis.call('GET', KEYS[4]) or '0')

if total_limit >= 0 and (total_count + total_pending) >= total_limit then
    return {0, 'total'}
end

if day_limit >= 0 and (day_count + day_pending) >= day_limit then
    return {0, 'day'}
end

if total_limit >= 0 then
    redis.call('INCR', KEYS[3])
    redis.call('EXPIRE', KEYS[3], reserve_ttl)
end

if day_limit >= 0 then
    redis.call('INCR', KEYS[4])
    redis.call('EXPIRE', KEYS[4], reserve_ttl)
end

return {1, 'ok'}
"""

COMMIT_AI_QUOTA_SCRIPT = """
local release_total = tonumber(ARGV[1])
local release_day = tonumber(ARGV[2])
local day_expire = tonumber(ARGV[3])
local reserve_ttl = tonumber(ARGV[4])

if release_total == 1 then
    local total_pending = tonumber(redis.call('GET', KEYS[3]) or '0')
    if total_pending <= 1 then
        redis.call('DEL', KEYS[3])
    else
        redis.call('DECR', KEYS[3])
        redis.call('EXPIRE', KEYS[3], reserve_ttl)
    end
end

if release_day == 1 then
    local day_pending = tonumber(redis.call('GET', KEYS[4]) or '0')
    if day_pending <= 1 then
        redis.call('DEL', KEYS[4])
    else
        redis.call('DECR', KEYS[4])
        redis.call('EXPIRE', KEYS[4], reserve_ttl)
    end
end

local total_count = redis.call('INCR', KEYS[1])
local day_count = redis.call('INCR', KEYS[2])
if day_expire > 0 then
    redis.call('EXPIRE', KEYS[2], day_expire)
end

return {total_count, day_count}
"""

ROLLBACK_AI_QUOTA_SCRIPT = """
local release_total = tonumber(ARGV[1])
local release_day = tonumber(ARGV[2])
local reserve_ttl = tonumber(ARGV[3])

if release_total == 1 then
    local total_pending = tonumber(redis.call('GET', KEYS[3]) or '0')
    if total_pending <= 1 then
        redis.call('DEL', KEYS[3])
    else
        redis.call('DECR', KEYS[3])
        redis.call('EXPIRE', KEYS[3], reserve_ttl)
    end
end

if release_day == 1 then
    local day_pending = tonumber(redis.call('GET', KEYS[4]) or '0')
    if day_pending <= 1 then
        redis.call('DEL', KEYS[4])
    else
        redis.call('DECR', KEYS[4])
        redis.call('EXPIRE', KEYS[4], reserve_ttl)
    end
end

return {1}
"""


class Gpt3Service:
    """GPT3 AI 对话服务。"""

    @staticmethod
    async def _get_redis() -> redis.Redis:
        """获取 Redis 客户端。"""
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @staticmethod
    async def check_mac_binding(clientid: str, macAddr: str) -> int:
        """检查 mac 地址是否已激活绑定，优先走缓存。"""
        redis_client = None
        cache_key = RedisKeys.mac_binding(clientid, macAddr)

        try:
            redis_client = await Gpt3Service._get_redis()
            cached_status = await redis_client.get(cache_key)
            if cached_status is not None:
                logger.info(
                    f"MAC binding cache hit: clientid={clientid}, macAddr={macAddr}"
                )
                return 1 if cached_status == "1" else -1
        except Exception as exc:
            logger.warning(f"MAC binding cache lookup failed: {exc}")

        try:
            mac_record = await Mac.filter(
                clientCode=clientid,
                macAddr=macAddr,
                active=1,
            ).first()
            cache_value = "1" if mac_record else "0"
            cache_ttl = (
                MAC_BINDING_CACHE_TTL_SECONDS
                if mac_record
                else MAC_BINDING_NEGATIVE_CACHE_TTL_SECONDS
            )
            if redis_client is not None:
                try:
                    await redis_client.setex(cache_key, cache_ttl, cache_value)
                except Exception as exc:
                    logger.warning(f"MAC binding cache backfill failed: {exc}")
            return 1 if mac_record else -1
        except Exception as exc:
            logger.exception(f"check_mac_binding failed: {exc}")
            return -1

    @staticmethod
    async def is_vip(userid: int) -> bool:
        """检查用户是否为 VIP，优先走缓存。"""
        try:
            return await UserService.is_vip(userid)
        except Exception as exc:
            logger.exception(f"is_vip check failed: {exc}")
            return False

    @staticmethod
    def _get_daily_expire_seconds() -> int:
        """计算当前到次日零点的过期秒数。"""
        current_time = time.time()
        tomorrow = time.localtime(current_time + 86400)
        tomorrow_midnight = time.mktime(
            (
                tomorrow.tm_year,
                tomorrow.tm_mon,
                tomorrow.tm_mday,
                0,
                0,
                0,
                tomorrow.tm_wday,
                tomorrow.tm_yday,
                tomorrow.tm_isdst,
            )
        )
        return max(int(tomorrow_midnight - current_time), 1)

    @staticmethod
    def _get_quota_limits(clientid: str, is_vip: bool) -> tuple[int | None, int | None]:
        """根据客户端和 VIP 状态计算限额。"""
        total_limit = None
        day_limit = None

        if clientid == PVMB_CLIENT_ID:
            if is_vip:
                day_limit = AI_DAY_LIMIT_VIP
            else:
                total_limit = AI_NUM_LIMIT_NORMAL
        elif not is_vip:
            day_limit = AI_DAY_LIMIT_NORMAL

        return total_limit, day_limit

    @classmethod
    async def _reserve_quota(
        cls,
        userid: int,
        clientid: str,
        total_limit: int | None,
        day_limit: int | None,
    ) -> str | None:
        """预占 AI 配额，失败时返回限制维度。"""
        redis_client = await cls._get_redis()
        reserve_result = await redis_client.eval(
            RESERVE_AI_QUOTA_SCRIPT,
            4,
            RedisKeys.ai_num(userid, clientid),
            RedisKeys.ai_day_num(userid),
            RedisKeys.ai_num_pending(userid, clientid),
            RedisKeys.ai_day_pending(userid),
            total_limit if total_limit is not None else -1,
            day_limit if day_limit is not None else -1,
            AI_QUOTA_RESERVATION_TTL_SECONDS,
        )
        if int(reserve_result[0]) == 1:
            return None
        return str(reserve_result[1])

    @classmethod
    async def _commit_quota(
        cls,
        userid: int,
        clientid: str,
        total_limit: int | None,
        day_limit: int | None,
    ) -> tuple[int, int]:
        """提交 AI 配额计数。"""
        redis_client = await cls._get_redis()
        commit_result = await redis_client.eval(
            COMMIT_AI_QUOTA_SCRIPT,
            4,
            RedisKeys.ai_num(userid, clientid),
            RedisKeys.ai_day_num(userid),
            RedisKeys.ai_num_pending(userid, clientid),
            RedisKeys.ai_day_pending(userid),
            1 if total_limit is not None else 0,
            1 if day_limit is not None else 0,
            cls._get_daily_expire_seconds(),
            AI_QUOTA_RESERVATION_TTL_SECONDS,
        )
        return int(commit_result[0]), int(commit_result[1])

    @classmethod
    async def _rollback_quota(
        cls,
        userid: int,
        clientid: str,
        total_limit: int | None,
        day_limit: int | None,
    ) -> None:
        """回滚 AI 配额预占。"""
        redis_client = await cls._get_redis()
        await redis_client.eval(
            ROLLBACK_AI_QUOTA_SCRIPT,
            4,
            RedisKeys.ai_num(userid, clientid),
            RedisKeys.ai_day_num(userid),
            RedisKeys.ai_num_pending(userid, clientid),
            RedisKeys.ai_day_pending(userid),
            1 if total_limit is not None else 0,
            1 if day_limit is not None else 0,
            AI_QUOTA_RESERVATION_TTL_SECONDS,
        )

    @staticmethod
    async def get_conversation_id(userid: int) -> str:
        """获取用户当前会话 ID。"""
        try:
            redis_client = await Gpt3Service._get_redis()
            conv_key = RedisKeys.gpt_conversation(userid)
            return await redis_client.get(conv_key) or ""
        except Exception as exc:
            logger.exception(f"get_conversation_id failed: {exc}")
            return ""

    @staticmethod
    async def save_conversation_id(userid: int, conversation_id: str) -> None:
        """保存会话 ID。"""
        try:
            redis_client = await Gpt3Service._get_redis()
            conv_key = RedisKeys.gpt_conversation(userid)
            await redis_client.setex(conv_key, 600, conversation_id)
        except Exception as exc:
            logger.exception(f"save_conversation_id failed: {exc}")

    @classmethod
    async def gpt(cls, params: dict) -> dict[str, Any]:
        """GPT3 AI 对话核心业务逻辑。"""
        userid = params["userid"]
        clientid = params["clientid"]
        macAddr = params["macAddr"]
        language = params.get("language", "")
        word = params["word"]

        if clientid != PVMB_CLIENT_ID:
            check_result = await cls.check_mac_binding(clientid, macAddr)
            if check_result != 1:
                logger.warning(
                    f"mac binding check failed: clientid={clientid}, macAddr={macAddr}, "
                    f"check_result={check_result}"
                )
                return {"code": check_result}

        if clientid not in CLIENT_DB_START and clientid != PVMB_CLIENT_ID:
            logger.warning(f"clientid not in whitelist: {clientid}")
            return {"code": -3}

        is_vip = await cls.is_vip(userid)
        total_limit, day_limit = cls._get_quota_limits(clientid, is_vip)

        quota_limit_type = await cls._reserve_quota(userid, clientid, total_limit, day_limit)
        if quota_limit_type == "total":
            logger.warning(f"AI usage limit exceeded: userid={userid}, clientid={clientid}")
            return {"code": -5}
        if quota_limit_type == "day":
            if clientid == PVMB_CLIENT_ID and is_vip:
                logger.warning(
                    f"Daily AI limit exceeded for VIP: userid={userid}, clientid={clientid}"
                )
                return {"code": -7, "max": AI_DAY_LIMIT_VIP}
            logger.warning(
                f"Daily AI limit exceeded for normal user: userid={userid}, clientid={clientid}"
            )
            return {"code": -6, "max": AI_DAY_LIMIT_NORMAL}

        conversation_id = await cls.get_conversation_id(userid)

        try:
            gpt_response, new_conversation_id = await gpt41mini_agent(
                word, str(userid), conversation_id, language
            )
        except Exception as exc:
            try:
                await cls._rollback_quota(userid, clientid, total_limit, day_limit)
            except Exception as rollback_exc:
                logger.exception(f"AI quota rollback failed: {rollback_exc}")
            logger.exception(f"GPT-4-mini call failed: {exc}")
            return {"code": -1, "error": "AI service unavailable"}

        try:
            total_count, day_count = await cls._commit_quota(
                userid,
                clientid,
                total_limit,
                day_limit,
            )
            logger.info(
                f"AI quota committed: userid={userid}, clientid={clientid}, "
                f"ai_num={total_count}, ai_day_num={day_count}"
            )
        except Exception as exc:
            logger.exception(f"AI quota commit failed: {exc}")

        if new_conversation_id:
            await cls.save_conversation_id(userid, new_conversation_id)

        logger.info(f"GPT3 request success: userid={userid}")
        return {"message": gpt_response, "code": 1}
