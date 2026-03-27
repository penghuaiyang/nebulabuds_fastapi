"""Wallpaper Service."""
from typing import Any, Dict, List, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import Wallpaper

logger = log_util.get_logger("wallpaper_service")


class WallpaperService:
    """壁纸服务类."""

    @classmethod
    async def get_wallpaper_list(
        cls,
        userid: int,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[int, Dict[str, Any]]:
        """获取壁纸列表.

        Args:
            userid: 用户ID
            page: 页码
            page_size: 每页数量

        Returns:
            Tuple[code, data]
        """
        try:
            offset = (page - 1) * page_size

            wallpapers = await Wallpaper.filter(
                userid=userid, is_deleted=False
            ).order_by("-created_at").limit(page_size).offset(offset).all()

            wallpaper_list = []
            for wp in wallpapers:
                wallpaper_list.append({
                    "id": wp.id,
                    "url": wp.url,
                    "thumbnail": wp.thumbnail,
                    "created_at": wp.created_at,
                })

            return 1, {"data": wallpaper_list}

        except Exception as exc:
            logger.exception(f"Get wallpaper list failed: {exc}")
            return -1, {"error": str(exc)}
