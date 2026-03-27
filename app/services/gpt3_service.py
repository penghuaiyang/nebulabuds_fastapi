"""GPT3 AI对话服务层

实现 AI 对话的核心业务逻辑，包括：
- mac 地址绑定检查
- AI 使用次数限制（普通用户/非普通用户）
- VIP 状态检查
- GPT-4-mini 对话调用
"""
import json
import time
from typing import Any, Optional

import redis.asyncio as redis

from app.common.utils.gpt4mini_utils import gpt41mini_agent
from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import Mac, User

logger = log_util.get_logger("gpt3_service")

# AI 日使用次数限制
AI_DAY_LIMIT_NORMAL = 20  # 普通用户每日限制
AI_DAY_LIMIT_VIP = 500   # VIP用户每日限制
PVMB_CLIENT_ID = "PVMB8x1N"  # PalmZen 平台客户端ID

# AI 次数限制（基于 ai_num Redis Key）
AI_NUM_LIMIT_NORMAL = 50  # 普通用户 AI 次数限制

# 客户端 db 起始配置
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


class Gpt3Service:
    """GPT3 AI对话服务"""

    @staticmethod
    async def _get_redis() -> redis.Redis:
        """获取 Redis 客户端"""
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @staticmethod
    async def check_mac_binding(clientid: str, macAddr: str) -> int:
        """检查 mac 地址是否已激活绑定

        Args:
            clientid: 客户端ID
            macAddr: mac地址

        Returns:
            int: 1=检查通过, 其他值为错误码
        """
        try:
            redis_client = await Gpt3Service._get_redis()

            # 使用 db=5 检查 mac 地址绑定状态
            # Mac 表结构: clientCode, macAddr, active, macType, deviceType 等
            mac_record = await Mac.filter(
                clientCode=clientid,
                macAddr=macAddr,
                active=1
            ).first()

            if mac_record:
                return 1
            else:
                return -1

        except Exception as exc:
            logger.exception(f"check_mac_binding failed: {exc}")
            return -1

    @staticmethod
    async def get_ai_num(userid: int, clientid: str) -> tuple[int, int]:
        """获取并递增 AI 使用次数

        Args:
            userid: 用户ID
            clientid: 客户端ID

        Returns:
            tuple: (当前AI次数, db编号)
        """
        try:
            redis_client = await Gpt3Service._get_redis()

            # 计算 db 编号
            ai_db = 8  # AI_NUM_DB
            if clientid in CLIENT_DB_START:
                ai_db = ai_db + CLIENT_DB_START[clientid]

            # 使用 Redis INCR 原子递增
            ai_num_key = RedisKeys.ai_num(userid, clientid)
            ai_num = await redis_client.incr(ai_num_key)

            return ai_num, ai_db

        except Exception as exc:
            logger.exception(f"get_ai_num failed: {exc}")
            return 0, 8

    @staticmethod
    async def is_vip(userid: int) -> bool:
        """检查用户是否为VIP

        Args:
            userid: 用户ID

        Returns:
            bool: 是否为VIP用户
        """
        try:
            # 从数据库获取用户信息
            user = await User.filter(userid=userid).first()
            if not user:
                return False

            vip = user.vip or 0
            if isinstance(vip, str):
                vip = int(vip) if vip else 0

            # 检查 VIP 过期时间
            current_time = int(time.time())
            return vip > current_time

        except Exception as exc:
            logger.exception(f"is_vip check failed: {exc}")
            return False

    @staticmethod
    async def get_ai_day_num(userid: int) -> int:
        """获取用户当日 AI 使用次数

        Args:
            userid: 用户ID

        Returns:
            int: 当日使用次数
        """
        try:
            redis_client = await Gpt3Service._get_redis()
            ai_day_key = RedisKeys.ai_day_num(userid)
            ai_day_num = await redis_client.get(ai_day_key)

            if ai_day_num is None:
                return 0
            return int(ai_day_num)

        except Exception as exc:
            logger.exception(f"get_ai_day_num failed: {exc}")
            return 0

    @staticmethod
    async def update_ai_day_num(userid: int) -> int:
        """更新用户当日 AI 使用次数

        Args:
            userid: 用户ID

        Returns:
            int: 更新后的当日使用次数
        """
        try:
            redis_client = await Gpt3Service._get_redis()
            ai_day_key = RedisKeys.ai_day_num(userid)

            # 获取次日零点时间戳，用于设置过期时间
            current_time = time.time()
            tomorrow = time.localtime(current_time + 86400)
            tomorrow_midnight = time.mktime(
                (tomorrow.tm_year, tomorrow.tm_mon, tomorrow.tm_mday, 0, 0, 0,
                 tomorrow.tm_wday, tomorrow.tm_yday, tomorrow.tm_isdst)
            )
            expire_seconds = int(tomorrow_midnight - current_time)

            # INCR 并设置过期时间
            ai_day_num = await redis_client.incr(ai_day_key)
            await redis_client.expire(ai_day_key, expire_seconds)

            return ai_day_num

        except Exception as exc:
            logger.exception(f"update_ai_day_num failed: {exc}")
            return 1

    @staticmethod
    async def get_conversation_id(userid: int) -> str:
        """获取用户当前会话 ID

        Args:
            userid: 用户ID

        Returns:
            str: 会话ID，空字符串表示新会话
        """
        try:
            redis_client = await Gpt3Service._get_redis()
            conv_key = RedisKeys.gpt_conversation(userid)
            return await redis_client.get(conv_key) or ""

        except Exception as exc:
            logger.exception(f"get_conversation_id failed: {exc}")
            return ""

    @staticmethod
    async def save_conversation_id(userid: int, conversation_id: str) -> None:
        """保存会话 ID

        Args:
            userid: 用户ID
            conversation_id: 会话ID
        """
        try:
            redis_client = await Gpt3Service._get_redis()
            conv_key = RedisKeys.gpt_conversation(userid)
            # 会话过期时间 600 秒（10分钟）
            await redis_client.setex(conv_key, 600, conversation_id)

        except Exception as exc:
            logger.exception(f"save_conversation_id failed: {exc}")

    @classmethod
    async def gpt(cls, params: dict) -> dict[str, Any]:
        """GPT3 AI 对话核心业务逻辑

        Args:
            params: 包含以下字段的字典
                - userid: 用户ID
                - clientid: 客户端ID
                - macAddr: mac地址
                - language: 语言设置
                - requestFrom: 请求来源
                - needTTS: 是否需要TTS
                - word: 对话内容

        Returns:
            dict: 响应结果，包含 code 和 message/error
        """
        userid = params["userid"]
        clientid = params["clientid"]
        macAddr = params["macAddr"]
        language = params.get("language", "")
        word = params["word"]

        # 1. 检查 mac 绑定（仅非 PalmZen 平台用户）
        if clientid != PVMB_CLIENT_ID:
            check_result = await cls.check_mac_binding(clientid, macAddr)
            if check_result != 1:
                logger.warning(
                    f"mac binding check failed: clientid={clientid}, macAddr={macAddr}, "
                    f"check_result={check_result}"
                )
                return {"code": check_result}

        # 2. 检查 clientid 是否在白名单中
        if clientid not in CLIENT_DB_START and clientid != PVMB_CLIENT_ID:
            logger.warning(f"clientid not in whitelist: {clientid}")
            return {"code": -3}

        # 3. 获取并递增 AI 使用次数（ai_num）
        ai_num, ai_db = await cls.get_ai_num(userid, clientid)
        logger.info(f"AI num: userid={userid}, ai_num={ai_num}, ai_db={ai_db}")

        # 4. PalmZen 平台用户检查 AI 次数限制
        if ai_num > AI_NUM_LIMIT_NORMAL and clientid == PVMB_CLIENT_ID:
            is_vip = await cls.is_vip(userid)
            if not is_vip:
                logger.warning(f"AI usage limit exceeded: userid={userid}, ai_num={ai_num}")
                return {"code": -5}  # 超过使用次数

        # 5. 检查当日使用次数限制
        ai_day_num = await cls.get_ai_day_num(userid)

        if clientid != PVMB_CLIENT_ID:
            # 非 PalmZen 平台用户
            is_vip = await cls.is_vip(userid)
            if not is_vip:
                if ai_day_num >= AI_DAY_LIMIT_NORMAL:
                    logger.warning(
                        f"Daily AI limit exceeded for normal user: "
                        f"userid={userid}, day_num={ai_day_num}"
                    )
                    return {"code": -6, "max": AI_DAY_LIMIT_NORMAL}
        else:
            # PalmZen 平台 VIP 用户
            is_vip = await cls.is_vip(userid)
            if is_vip:
                if ai_day_num >= AI_DAY_LIMIT_VIP:
                    logger.warning(
                        f"Daily AI limit exceeded for VIP: userid={userid}, day_num={ai_day_num}"
                    )
                    return {"code": -7, "max": AI_DAY_LIMIT_VIP}

        # 6. 更新当日 AI 使用次数
        await cls.update_ai_day_num(userid)

        # 7. 获取/创建会话 ID
        conversation_id = await cls.get_conversation_id(userid)

        # 8. 调用 GPT-4-mini Agent
        try:
            gpt_response, new_conversation_id = await gpt41mini_agent(
                word, str(userid), conversation_id, language
            )
        except Exception as exc:
            logger.exception(f"GPT-4-mini call failed: {exc}")
            return {"code": -1, "error": "AI service unavailable"}

        # 9. 保存新的会话 ID
        if new_conversation_id:
            await cls.save_conversation_id(userid, new_conversation_id)

        logger.info(f"GPT3 request success: userid={userid}")
        return {"message": gpt_response, "code": 1}
