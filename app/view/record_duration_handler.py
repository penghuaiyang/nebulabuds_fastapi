"""Record Duration 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.record_duration_schema import RecordDurationRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.record_duration_service import RecordDurationService

logger = log_util.get_logger("record_duration_handler")


@auth_required
@check_params
async def record_duration(data: RecordDurationRequestSchema, request: Request) -> dict[str, Any]:
    """处理录音时长记录请求."""
    code, result = await RecordDurationService.add_duration(
        clientid=data.clientid,
        userid=data.userid,
        duration=data.duration,
        duration_type=data.durationType,
        is_trtc=data.isTRTC or 0,
        active_code=data.activeCode,
    )

    return result
