"""V2Active 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.v2_active_schema import V2ActiveRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.v2_active_service import V2ActiveService

logger = log_util.get_logger("v2_active_handler")


@auth_required
@check_params
async def v2_active(data: V2ActiveRequestSchema, request: Request) -> dict[str, Any]:
    """处理 V2 设备激活请求."""
    try:
        code, result = await V2ActiveService.activate(
            bt_name=data.bt_name,
            clientid=data.clientid,
            mac_addr=data.macAddr,
            userid=data.userid,
        )

        if code == 1 or code == 2:
            return result

        return {"code": code}

    except Exception as exc:
        logger.exception(f"V2Active error: {exc}")
        return {"code": -3, "error": str(exc)}
