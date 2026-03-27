"""Text2Img 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.text2img_schema import Text2ImgRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.text2img_service import Text2ImgService

logger = log_util.get_logger("text2img_handler")


@auth_required
@check_params
async def text2img(data: Text2ImgRequestSchema, request: Request) -> dict[str, Any]:
    """处理文字生成图片请求."""
    code, result = await Text2ImgService.generate(
        clientid=data.clientid,
        mac_addr=data.macAddr,
        userid=data.userid,
        prompt=data.prompt,
        size=data.size,
    )

    if code == 1:
        return result

    return {"code": code, "error": result.get("error", "generate failed")}
