"""Record Duration Service."""
import time
from typing import Any, Dict, Optional, Tuple

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys

logger = log_util.get_logger("record_duration_service")

RECORD_DURATION_DB = 7
DURATION_SUPER_DB = 11
RECORD_REST_DB = 29
RTC_FREE_DB = 31
ONE_YEAR_NO_DEDUCTION_DB = 32

SUPER_CLIENT_IDS = ["WBvgcoct", "VYb6En3x"]

DAY_FREE_REST_TIME_MAP = {
    "WBvgcoct": 3600,
    "VYb6En3x": 3600 * 3,
}


class RecordDurationService:
    """录音时长记录服务类."""

    @classmethod
    async def add_duration(
        cls,
        clientid: str,
        userid: int,
        duration: int,
        duration_type: Optional[int] = None,
        is_trtc: int = 0,
        active_code: Optional[str] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        """增加录音时长记录.

        Args:
            clientid: 客户端ID
            userid: 用户ID
            duration: 时长（秒）
            duration_type: 时长类型 1=现场录音 2=同声传译 3=面对面翻译
            is_trtc: 是否音视频通话
            active_code: 激活码

        Returns:
            Tuple[code, data]
        """
        try:
            redis_client = await get_redis_client()
            if redis_client is None:
                return -1, {"error": "Redis not available"}

            duration_key = RedisKeys.record_duration(userid)
            old_duration = await redis_client.get(duration_key)

            if not old_duration:
                new_duration = duration
                await redis_client.set(duration_key, duration)
            else:
                old_duration = int(old_duration)
                duration = int(duration)
                new_duration = old_duration + duration
                await redis_client.set(duration_key, new_duration)

            rest_time = await cls._calculate_rest_time(
                redis_client, userid, duration, duration_type, is_trtc, clientid
            )

            return 1, {
                "duration": new_duration,
                "restTime": rest_time,
            }

        except Exception as exc:
            logger.exception(f"Add duration failed: {exc}")
            return -1, {"error": str(exc)}

    @classmethod
    async def _calculate_rest_time(
        cls,
        redis_client,
        userid: int,
        duration: int,
        duration_type: Optional[int],
        is_trtc: int,
        clientid: str,
    ) -> int:
        """计算录音剩余时长."""
        rest_key = RedisKeys.record_rest(userid)
        rest_time = await redis_client.get(rest_key)

        if not rest_time:
            rest_time = 0
        else:
            rest_time = int(rest_time)

        rest_time = rest_time - int(duration)
        if rest_time < 0:
            rest_time = 0

        await redis_client.set(rest_key, rest_time)
        return rest_time
