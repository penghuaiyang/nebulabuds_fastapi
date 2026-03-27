"""文字生成图片服务."""
import base64
import random
from typing import Tuple

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys

logger = log_util.get_logger("text2img_service")

# palmzen 平台 clientid
PALMZEN_CLIENT_ID = "PVMB8x1N"

# 普通用户每日限制
FREE_DAY_LIMIT = 5
# VIP 用户每日限制
VIP_DAY_LIMIT = 20
# palmzen 每日限制
PALMZEN_DAY_LIMIT = 15


class Text2ImgService:
    """文字生成图片服务类."""

    @staticmethod
    async def _get_redis():
        """获取 Redis 客户端."""
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @classmethod
    async def generate(
        cls,
        clientid: str,
        mac_addr: str,
        userid: int,
        prompt: str,
        size: int = 0,
    ) -> Tuple[int, dict]:
        """处理文字生成图片请求.

        Args:
            clientid: 客户端ID
            mac_addr: MAC地址
            userid: 用户ID
            prompt: 生成提示词
            size: 图片尺寸 0=正方形, 1=横屏, 2=竖屏

        Returns:
            Tuple[code, data]
        """
        try:
            # TODO: 实现 MAC 验证逻辑
            if clientid != PALMZEN_CLIENT_ID:
                pass

            # 设置图片尺寸
            if size == 1:
                width, height = 768, 422
            elif size == 2:
                width, height = 422, 768
            else:
                width, height = 768, 768

            # TODO: 实现图片生成逻辑（调用 Ark 或 Stable Diffusion）
            # 目前返回占位数据
            return -1, {
                "code": -1,
                "message": "Image generation not implemented yet",
            }

        except Exception as exc:
            logger.exception(f"Text2Img error: {exc}")
            return -1, {"error": str(exc), "code": -1}
