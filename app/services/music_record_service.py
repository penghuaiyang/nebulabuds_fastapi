"""Music Record Service."""
from typing import Any, Dict, Tuple

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys

logger = log_util.get_logger("music_record_service")

MUSIC_NUM_DB_BASE = 10


class MusicRecordService:
    """音乐记录服务类."""

    @classmethod
    async def increment_music_count(
        cls,
        clientid: str,
        userid: int,
    ) -> Tuple[int, Dict[str, Any]]:
        """增加音乐使用次数.

        Args:
            clientid: 客户端ID
            userid: 用户ID

        Returns:
            Tuple[code, data]
        """
        try:
            redis_client = await get_redis_client()
            if redis_client is None:
                return -1, {"error": "Redis not available"}

            key = RedisKeys.music_num(userid)
            old_num = await redis_client.get(key)

            if not old_num:
                num = 1
                await redis_client.set(key, 1)
            else:
                old_num = int(old_num)
                num = old_num + 1
                await redis_client.set(key, num)

            return 1, {"num": num}

        except Exception as exc:
            logger.exception(f"Increment music count failed: {exc}")
            return -1, {"error": str(exc)}
