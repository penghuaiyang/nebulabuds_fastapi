"""Music Favorite Service."""
import time
from typing import Any, Dict, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import Music, UserMusicFavorites

logger = log_util.get_logger("music_favorite_service")

USER_DB = 0


class MusicFavoriteService:
    """音乐收藏服务类."""

    @classmethod
    async def toggle_favorite(
        cls,
        userid: int,
        music_id: int,
        action: str,
    ) -> Tuple[int, Dict[str, Any]]:
        """切换音乐收藏状态.

        Args:
            userid: 用户ID
            music_id: 音乐ID
            action: 操作 add=收藏 remove=取消

        Returns:
            Tuple[code, data]
        """
        try:
            music = await Music.filter(id=music_id, is_active=True).first()
            if not music:
                return -2, {"error": "Music not found or inactive"}

            if action == "add":
                user_is_vip = await cls._is_vip_user(userid)
                if music.is_vip and not user_is_vip:
                    return -3, {"error": "VIP required"}

                await UserMusicFavorites.get_or_create(
                    userid=userid,
                    music=music,
                    defaults={"created_at": int(time.time() * 1000)},
                )
                logger.info(f"Music favorited: userid={userid}, music_id={music_id}")
                return 1, {"code": 1, "message": "收藏成功"}

            deleted_count = await UserMusicFavorites.filter(
                userid=userid, music=music
            ).delete()
            logger.info(f"Music unfavorited: userid={userid}, music_id={music_id}, deleted={deleted_count}")
            return 1, {"code": 1, "message": "取消收藏成功"}

        except Exception as exc:
            logger.exception(f"Music favorite toggle failed: {exc}")
            return -1, {"error": str(exc)}

    @staticmethod
    async def _is_vip_user(userid: int) -> bool:
        """检查用户是否为VIP."""
        from app.db.redis import get_redis_client

        redis_client = await get_redis_client()
        if redis_client is None:
            return False

        try:
            vip_key = f"{USER_DB}:user:{userid}:vip"
            vip_ts = await redis_client.get(vip_key)
            if not vip_ts:
                return False
            vip_value = int(vip_ts)
            return vip_value > int(time.time())
        except Exception:
            return False
