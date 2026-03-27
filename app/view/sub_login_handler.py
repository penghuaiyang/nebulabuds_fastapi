"""SubLogin 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.sub_login_schema import SubLoginRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.sub_login_service import SubLoginService

logger = log_util.get_logger("sub_login_handler")


@auth_required
@check_params
async def sub_login(data: SubLoginRequestSchema, request: Request) -> dict[str, Any]:
    """处理 Google/X 订阅登录请求."""
    code, result = await SubLoginService.login(
        sub=data.sub,
        userid=data.userid,
        sub_type=data.subType,
    )

    if code == 1:
        return {
            "code": 1,
            "userid": result.get("userid"),
            "deviceid": result.get("deviceid"),
        }

    if code == -4:
        return {"code": -4, "error": "subType error"}

    return {"code": code, "error": result.get("error", "login failed")}
