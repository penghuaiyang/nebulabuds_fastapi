"""Active 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.active_schema import ActiveRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.active_service import ActiveService

logger = log_util.get_logger("active_handler")


@auth_required
@check_params
async def active(data: ActiveRequestSchema, request: Request) -> dict[str, Any]:
    """处理 V1 设备激活请求."""
    code, result = await ActiveService.activate(
        bt_name=data.bt_name,
        clientid=data.clientid,
        mac_addr=data.macAddr,
        userid=data.userid,
    )

    return result
