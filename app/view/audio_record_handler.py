"""Audio Record 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.audio_record_schema import AudioRecordRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.audio_record_service import AudioRecordService

logger = log_util.get_logger("audio_record_handler")


@auth_required
@check_params
async def audio_record(data: AudioRecordRequestSchema, request: Request) -> dict[str, Any]:
    """处理音频记录查询请求."""
    code, result = await AudioRecordService.get_records(
        clientid=data.clientid,
        mac_addr=data.macAddr,
        userid=data.userid,
        page=data.page,
    )

    return result
