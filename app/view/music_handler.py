"""Music 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.music_schema import MusicRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.music_service import MusicService

logger = log_util.get_logger("music_handler")


@auth_required
@check_params
async def music(data: MusicRequestSchema, request: Request) -> dict[str, Any]:
    """处理音乐列表查询请求."""
    code, result = await MusicService.get_music_list(
        language_code=data.language_code,
    )

    return result
