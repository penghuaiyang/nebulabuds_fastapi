"""Wallpaper Delete 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.wallpaper_delete_schema import WallpaperDeleteRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.wallpaper_delete_service import WallpaperDeleteService

logger = log_util.get_logger("wallpaper_delete_handler")


@auth_required
@check_params
async def wallpaper_delete(data: WallpaperDeleteRequestSchema, request: Request) -> dict[str, Any]:
    """处理壁纸删除请求."""
    code, result = await WallpaperDeleteService.delete_wallpaper(
        userid=data.userid,
        wallpaper_id=data.wallpaperid,
    )

    return result
