"""Img2Img 图片生成图片服务."""
from typing import Tuple

from app.common.utils.log_utils import log_util

logger = log_util.get_logger("img2img_service")

# palmzen 平台 clientid
PALMZEN_CLIENT_ID = "PVMB8x1N"

# 普通用户每日限制
FREE_DAY_LIMIT = 5
# VIP 用户每日限制
VIP_DAY_LIMIT = 20
# palmzen 每日限制
PALMZEN_DAY_LIMIT = 15


class Img2ImgService:
    """图片生成图片服务类."""

    @classmethod
    async def generate(
        cls,
        clientid: str,
        userid: int,
        mac_addr: str,
        prompt: str,
        image_data: bytes,
        format: str = "jpeg",
    ) -> Tuple[int, dict]:
        """处理图片生成图片请求.

        Args:
            clientid: 客户端ID
            userid: 用户ID
            mac_addr: MAC地址
            prompt: 生成提示词
            image_data: 输入图片数据
            format: 图片格式

        Returns:
            Tuple[code, data]
        """
        try:
            # TODO: 实现 MAC 验证逻辑
            if clientid != PALMZEN_CLIENT_ID:
                pass

            # TODO: 实现图片生成逻辑（调用 Ark 或 Stable Diffusion）
            # 目前返回占位数据
            return -1, {
                "code": -1,
                "message": "Image generation not implemented yet",
            }

        except Exception as exc:
            logger.exception(f"Img2Img error: {exc}")
            return -2, {"error": str(exc), "code": -2}
