"""Music Play Report Service."""
from typing import Any, Dict, Tuple

from packaging import version as pkg_version

from app.common.utils.log_utils import log_util
from app.models.models import Music

logger = log_util.get_logger("music_play_report_service")

MUSIC_PLAY_REPORT_TTL = 3600


class MusicPlayReportService:
    """音乐播放上报服务类."""

    @classmethod
    async def report_play(
        cls,
        userid: int,
        music_id: int,
    ) -> Tuple[int, Dict[str, Any]]:
        """上报音乐播放.

        Args:
            userid: 用户ID
            music_id: 音乐ID

        Returns:
            Tuple[code, data]
        """
        try:
            music = await Music.filter(id=music_id, is_active=True).first()
            if not music:
                return -2, {"error": "Music not found or inactive"}

            if not await cls._hit_play_limit(userid, music_id):
                return -3, {"error": "重复上报"}

            await Music.filter(id=music_id).update(play_count=music.play_count + 1)

            return 1, {"code": 1, "message": "success"}

        except Exception as exc:
            logger.exception(f"Music play report failed: {exc}")
            return -1, {"error": str(exc)}

    @staticmethod
    async def _hit_play_limit(userid: int, music_id: int) -> bool:
        """检查是否重复上报."""
        from app.db.redis import get_redis_client

        redis_client = await get_redis_client()
        if redis_client is None:
            return True

        try:
            key = f"music:play:{userid}:{music_id}"
            existed = await redis_client.exists(key)
            if existed:
                return False
            await redis_client.set(key, "1", ex=MUSIC_PLAY_REPORT_TTL)
            return True
        except Exception:
            return True
