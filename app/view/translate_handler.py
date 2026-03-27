"""Translate 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.translate_schema import TranslateRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.translate_service import TranslateService

logger = log_util.get_logger("translate_handler")


@auth_required
@check_params
async def translate(data: TranslateRequestSchema, request: Request) -> dict[str, Any]:
    """处理翻译请求."""
    code, result = await TranslateService.translate(
        clientid=data.clientid,
        mac_addr=data.macAddr,
        userid=data.userid,
        text=data.text,
        language=data.language,
        source_language=data.source_language or "",
    )

    if code == 1:
        return result

    return {"code": code, "error": result.get("error", "translate failed")}
