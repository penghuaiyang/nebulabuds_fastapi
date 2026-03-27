"""Summary 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.summary_schema import SummaryRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.summary_service import SummaryService

logger = log_util.get_logger("summary_handler")


@auth_required
@check_params
async def summary(data: SummaryRequestSchema, request: Request) -> dict[str, Any]:
    """处理内容总结请求."""
    code, result = await SummaryService.summarize(
        clientid=data.clientid,
        mac_addr=data.macAddr,
        userid=data.userid,
        word=data.word,
    )

    if code == 1:
        return result

    return {"code": code, "error": result.get("error", "summary failed")}
