"""UpdateClientidAndMac 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.update_clientid_mac_schema import UpdateClientidAndMacRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.device_service import DeviceService

logger = log_util.get_logger("update_clientid_mac_handler")


@auth_required
@check_params
async def update_clientid_mac(data: UpdateClientidAndMacRequestSchema, request: Request) -> dict[str, Any]:
    """处理更新客户端ID和MAC地址请求."""
    code, message = await DeviceService.update_clientid_and_mac(
        userid=data.userid,
        clientid=data.clientid,
        mac_addr=data.macAddr,
    )

    if code == 1:
        return {"code": 1, "message": "ok"}

    return {"code": code, "error": message}
