"""Music Favorite List 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.music_favorite_list_schema import MusicFavoriteListRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.music_favorite_list_service import MusicFavoriteListService

logger = log_util.get_logger("music_favorite_list_handler")


@auth_required
@check_params
async def music_favorite_list(data: MusicFavoriteListRequestSchema, request: Request) -> dict[str, Any]:
    """处理音乐收藏列表查询请求."""
    code, result = await MusicFavoriteListService.get_favorite_list(
        userid=data.userid,
        page=data.page,
        page_size=data.pageSize,
    )

    return result
