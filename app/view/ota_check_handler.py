"""OTA Check 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.ota_check_schema import OTARequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.ota_check_service import OTACheckService

logger = log_util.get_logger("ota_check_handler")


@auth_required
@check_params
async def ota_check(data: OTARequestSchema, request: Request) -> dict[str, Any]:
    """处理OTA检查请求."""
    code, result = await OTACheckService.check_update(
        firmware_id=data.firmware_id,
        current_version=data.current_version,
    )

    return result
