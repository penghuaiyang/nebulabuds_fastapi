"""Music Record 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.music_record_schema import MusicRecordRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.music_record_service import MusicRecordService

logger = log_util.get_logger("music_record_handler")


@auth_required
@check_params
async def music_record(data: MusicRecordRequestSchema, request: Request) -> dict[str, Any]:
    """处理音乐记录请求."""
    code, result = await MusicRecordService.increment_music_count(
        clientid=data.clientid,
        userid=data.userid,
    )

    return result
