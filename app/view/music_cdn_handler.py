"""Music CDN 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.music_cdn_schema import MusicCDNRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.music_cdn_service import MusicCDNService

logger = log_util.get_logger("music_cdn_handler")


@auth_required
@check_params
async def music_cdn(data: MusicCDNRequestSchema, request: Request) -> dict[str, Any]:
    """处理音乐CDN配置查询请求."""
    code, result = await MusicCDNService.get_cdn_config(
        language_code=data.language_code,
    )

    return result
