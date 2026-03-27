"""Wallpaper List 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.wallpaper_list_schema import WallpaperListRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.wallpaper_service import WallpaperService

logger = log_util.get_logger("wallpaper_list_handler")


@auth_required
@check_params
async def wallpaper_list(data: WallpaperListRequestSchema, request: Request) -> dict[str, Any]:
    """处理壁纸列表查询请求."""
    code, result = await WallpaperService.get_wallpaper_list(
        userid=data.userid,
        page=data.page,
        page_size=data.pageSize,
    )

    return result
