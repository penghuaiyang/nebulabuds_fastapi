"""Wallpaper Delete Service."""
import time
from typing import Any, Dict, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import Wallpaper

logger = log_util.get_logger("wallpaper_delete_service")


class WallpaperDeleteService:
    """壁纸删除服务类."""

    @classmethod
    async def delete_wallpaper(
        cls,
        userid: int,
        wallpaper_id: int,
    ) -> Tuple[int, Dict[str, Any]]:
        """删除壁纸.

        Args:
            userid: 用户ID
            wallpaper_id: 壁纸ID

        Returns:
            Tuple[code, data]
        """
        try:
            wallpaper = await Wallpaper.filter(id=wallpaper_id, userid=userid).first()

            if wallpaper:
                wallpaper.is_deleted = True
                wallpaper.updated_at = int(time.time() * 1000)
                await wallpaper.save()

            return 1, {"code": 1}

        except Exception as exc:
            logger.exception(f"Delete wallpaper failed: {exc}")
            return -1, {"error": str(exc)}
