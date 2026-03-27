"""Weather Info Service."""
from typing import Any, Dict, Tuple

from app.common.utils.log_utils import log_util

logger = log_util.get_logger("weather_info_service")


class WeatherInfoService:
    """天气信息服务类."""

    @classmethod
    async def get_weather(
        cls,
        lat: str,
        lng: str,
        time: str,
    ) -> Tuple[int, Dict[str, Any]]:
        """获取天气信息.

        Args:
            lat: 纬度
            lng: 经度
            time: 时间

        Returns:
            Tuple[code, data]
        """
        try:
            return 1, {"weather_info": {}}

        except Exception as exc:
            logger.exception(f"Get weather failed: {exc}")
            return -1, {"error": str(exc)}
