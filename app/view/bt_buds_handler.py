"""BTBuds 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.bt_buds_schema import BTBudsRequestSchema
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.bt_buds_service import BTBudsService

logger = log_util.get_logger("bt_buds_handler")


@auth_required
async def bt_buds(data: BTBudsRequestSchema, request: Request) -> dict[str, Any]:
    """处理蓝牙耳机设备查询请求."""
    code, result = await BTBudsService.query_buds(
        userid=data.userid,
        clientid=data.clientid,
        bt_names=data.bt_name,
        current_bt_name=data.current_bt_name,
    )

    if code == 1:
        return result

    return {"code": code, "error": result.get("error", "query failed")}
