"""Music Favorite 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.music_favorite_schema import MusicFavoriteRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.music_favorite_service import MusicFavoriteService

logger = log_util.get_logger("music_favorite_handler")


@auth_required
@check_params
async def music_favorite(data: MusicFavoriteRequestSchema, request: Request) -> dict[str, Any]:
    """处理音乐收藏请求."""
    code, result = await MusicFavoriteService.toggle_favorite(
        userid=data.userid,
        music_id=data.music_id,
        action=data.action,
    )

    return result
