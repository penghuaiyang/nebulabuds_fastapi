"""翻译服务."""
import httpx
from typing import Optional, Tuple

from app.common.llm.translate import translate_text
from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys

logger = log_util.get_logger("translate_service")

# palmzen 平台 clientid（不需要 MAC 验证）
PALMZEN_CLIENT_ID = "PVMB8x1N"


class TranslateService:
    """翻译服务类."""

    @staticmethod
    async def _get_redis():
        """获取 Redis 客户端."""
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @classmethod
    async def translate(
        cls,
        clientid: str,
        mac_addr: str,
        userid: int,
        text: str,
        language: str,
        source_language: str = "",
    ) -> Tuple[int, dict]:
        """处理翻译请求.

        Args:
            clientid: 客户端ID
            mac_addr: MAC地址
            userid: 用户ID
            text: 待翻译文本
            language: 目标语言
            source_language: 源语言

        Returns:
            Tuple[code, data]
            - code=1: 翻译成功
            - code=-1: 翻译失败
            - code=-3: MAC验证失败
            - code=0: 参数错误
        """
        try:
            # palmzen 平台不需要 MAC 验证
            if clientid != PALMZEN_CLIENT_ID:
                # TODO: 需要实现 MAC 验证逻辑
                # mac_check = await cls._check_mac(clientid, mac_addr)
                # if mac_check != 1:
                #     return mac_check, {"code": mac_check}
                pass

            # 执行翻译
            translated_text = await translate_text(text, language)

            return 1, {
                "text": translated_text,
                "language": language,
                "code": 1,
            }

        except Exception as exc:
            logger.exception(f"Translate error: {exc}")
            return -1, {"error": str(exc), "code": -1}
