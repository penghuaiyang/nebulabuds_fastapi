"""Upload Wallpaper Service."""
import os
import time
import random
from datetime import datetime
from typing import Any, Dict, Tuple

from fastapi import UploadFile

from app.common.utils.log_utils import log_util
from app.models.models import Wallpaper

logger = log_util.get_logger("upload_wallpaper_service")

UPLOAD_PATH = "/var/local/buds/wallpaper/"


class UploadWallpaperService:
    """壁纸上传服务类."""

    @classmethod
    async def upload_wallpaper(
        cls,
        userid: int,
        wallpaper_file: UploadFile,
    ) -> Tuple[int, Dict[str, Any]]:
        """上传壁纸文件并创建记录.

        Args:
            userid: 用户ID
            wallpaper_file: 壁纸文件

        Returns:
            Tuple[code, data]
        """
        try:
            file_ext = os.path.splitext(wallpaper_file.filename)[1] if wallpaper_file.filename else ".jpg"
            fname = f"{random.randint(0, 2 ** 32 - 1)}{file_ext}"

            wallpaper_path = os.path.join(UPLOAD_PATH, fname)
            os.makedirs(UPLOAD_PATH, exist_ok=True)

            content_bytes = await wallpaper_file.read()
            with open(wallpaper_path, 'wb') as fh:
                fh.write(content_bytes)

            now = int(time.time() * 1000)

            wallpaper_obj = await Wallpaper.create(
                userid=userid,
                url=f"/wallpaper/{fname}",
                thumbnail=None,
                is_deleted=False,
                created_at=now,
                updated_at=now,
            )

            return 1, {"code": 1}

        except Exception as exc:
            logger.exception(f"Upload wallpaper failed: {exc}")
            return -1, {"error": str(exc)}
