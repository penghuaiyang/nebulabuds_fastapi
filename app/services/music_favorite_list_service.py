"""Music Favorite List Service."""
from typing import Any, Dict, List, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import Music, UserMusicFavorites

logger = log_util.get_logger("music_favorite_list_service")


class MusicFavoriteListService:
    """音乐收藏列表服务类."""

    @classmethod
    async def get_favorite_list(
        cls,
        userid: int,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[int, Dict[str, Any]]:
        """获取音乐收藏列表.

        Args:
            userid: 用户ID
            page: 页码
            page_size: 每页数量

        Returns:
            Tuple[code, data]
        """
        try:
            offset = (page - 1) * page_size

            favorites = await UserMusicFavorites.filter(userid=userid).order_by("-created_at").limit(page_size).offset(offset).all()

            music_list = []
            for fav in favorites:
                music = await Music.filter(id=fav.music.id, is_active=True).first()
                if music:
                    music_list.append(await music.to_dict())

            return 1, {"music": music_list}

        except Exception as exc:
            logger.exception(f"Get favorite list failed: {exc}")
            return -1, {"error": str(exc)}
