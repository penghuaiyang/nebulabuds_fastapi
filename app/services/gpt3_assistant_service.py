"""GPT3 助手服务."""
import httpx
from typing import Tuple

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys

logger = log_util.get_logger("gpt3_assistant_service")

# palmzen 平台 clientid
PALMZEN_CLIENT_ID = "PVMB8x1N"

# API 配置
CHINESE_API_KEY = "app-Ppv4XA0pZzNHLBWgaDT6f0jy"
ENGLISH_API_KEY = "app-xKuJ2xPJHqtQxSlxgzQYN4Vg"
API_URL = "http://124.222.17.175:81/v1/chat-messages"


class Gpt3AssistantService:
    """GPT3 助手服务类."""

    @staticmethod
    async def _get_redis():
        """获取 Redis 客户端."""
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @classmethod
    async def chat(
        cls,
        userid: int,
        clientid: str,
        mac_addr: str,
        request_from: str,
        assistanid: str,
        is_cn: int,
        prompt: str,
        language_code: str,
        need_tts: int,
        word: str,
    ) -> Tuple[int, dict]:
        """处理 GPT3 助手对话请求.

        Args:
            userid: 用户ID
            clientid: 客户端ID
            mac_addr: MAC地址
            request_from: 请求来源
            assistanid: 助手ID
            is_cn: 是否中文
            prompt: 系统提示词
            language_code: 语言代码
            need_tts: 是否需要TTS
            word: 用户输入

        Returns:
            Tuple[code, data]
        """
        try:
            # TODO: 实现 MAC 验证逻辑
            if clientid != PALMZEN_CLIENT_ID:
                pass

            # 选择 API Key
            api_key = CHINESE_API_KEY if is_cn else ENGLISH_API_KEY

            # TODO: 实现助手对话逻辑
            # 目前返回占位数据
            return 1, {
                "message": word,  # 占位
                "code": 1,
            }

        except Exception as exc:
            logger.exception(f"Gpt3Assistant error: {exc}")
            return -1, {"error": str(exc), "code": -1}
