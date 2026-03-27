"""Img2Img 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.img2img_schema import Img2ImgRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.img2img_service import Img2ImgService

logger = log_util.get_logger("img2img_handler")


@auth_required
@check_params
async def img2img(data: Img2ImgRequestSchema, request: Request) -> dict[str, Any]:
    """处理图片生成图片请求."""
    # 注意：此接口需要处理文件上传，暂时返回占位
    return {
        "code": -1,
        "message": "File upload handler not implemented yet",
    }
