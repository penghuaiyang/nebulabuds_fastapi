"""Music Play Report 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.music_play_report_schema import MusicPlayReportRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.music_play_report_service import MusicPlayReportService

logger = log_util.get_logger("music_play_report_handler")


@auth_required
@check_params
async def music_play_report(data: MusicPlayReportRequestSchema, request: Request) -> dict[str, Any]:
    """处理音乐播放上报请求."""
    code, result = await MusicPlayReportService.report_play(
        userid=data.userid,
        music_id=data.music_id,
    )

    return result
