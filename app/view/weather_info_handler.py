"""Weather Info 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.weather_info_schema import WeatherInfoRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import no_auth_required
from app.common.utils.log_utils import log_util
from app.services.weather_info_service import WeatherInfoService

logger = log_util.get_logger("weather_info_handler")


@no_auth_required
@check_params
async def weather_info(data: WeatherInfoRequestSchema, request: Request) -> dict[str, Any]:
    """处理天气信息查询请求."""
    code, result = await WeatherInfoService.get_weather(
        lat=data.lat,
        lng=data.lng,
        time=data.time,
    )

    return result
