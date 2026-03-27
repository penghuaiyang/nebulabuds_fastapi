"""Music Categories List 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.music_categories_list_schema import MusicCategoriesListRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.music_categories_list_service import MusicCategoriesListService

logger = log_util.get_logger("music_categories_list_handler")


@auth_required
@check_params
async def music_categories_list(data: MusicCategoriesListRequestSchema, request: Request) -> dict[str, Any]:
    """处理音乐分类列表查询请求."""
    code, result = await MusicCategoriesListService.get_categories_list()

    return result
