"""Assistant Record 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.assistant_record_schema import AssistantRecordRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.assistant_record_service import AssistantRecordService

logger = log_util.get_logger("assistant_record_handler")


@auth_required
@check_params
async def assistant_record(data: AssistantRecordRequestSchema, request: Request) -> dict[str, Any]:
    """处理助手记录查询请求."""
    code, result = await AssistantRecordService.get_records(
        clientid=data.clientid,
        userid=data.userid,
        language_code=data.languageCode,
    )

    return result
