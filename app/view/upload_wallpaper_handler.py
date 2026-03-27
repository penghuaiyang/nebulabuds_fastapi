"""Upload Wallpaper 接口处理器."""
from typing import Any

from fastapi import File, Form, Request, UploadFile

from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.upload_wallpaper_service import UploadWallpaperService

logger = log_util.get_logger("upload_wallpaper_handler")


@auth_required
async def upload_wallpaper(
    userid: int = Form(..., description="用户ID"),
    pass_: str = Form(..., alias="pass", description="签名校验"),
    wallpaper: UploadFile = File(..., description="壁纸文件"),
    request: Request = None,
) -> dict[str, Any]:
    """处理壁纸上传请求."""
    code, result = await UploadWallpaperService.upload_wallpaper(
        userid=userid,
        wallpaper_file=wallpaper,
    )

    return result
