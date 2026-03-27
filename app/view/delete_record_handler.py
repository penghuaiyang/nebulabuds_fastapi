"""Delete Record 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.delete_record_schema import DeleteRecordRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.delete_record_service import DeleteRecordService

logger = log_util.get_logger("delete_record_handler")


@auth_required
@check_params
async def delete_record(data: DeleteRecordRequestSchema, request: Request) -> dict[str, Any]:
    """处理删除音频记录请求."""
    code, result = await DeleteRecordService.delete_audio_record(
        clientid=data.clientid,
        mac_addr=data.macAddr,
        audioid=data.audioid,
        userid=data.userid,
    )

    return result
