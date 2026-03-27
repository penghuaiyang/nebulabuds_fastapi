"""AppleLogin 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.apple_login_schema import AppleLoginRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import no_auth_required
from app.common.utils.log_utils import log_util
from app.services.apple_login_service import AppleLoginService

logger = log_util.get_logger("apple_login_handler")


@no_auth_required
@check_params
async def apple_login(data: AppleLoginRequestSchema, request: Request) -> dict[str, Any]:
    """处理 Apple 登录请求."""
    code, result = await AppleLoginService.login(
        userid=data.userid,
        id_token=data.id_token,
    )

    if code == 1:
        return {
            "code": 1,
            "userid": result.get("userid"),
            "deviceid": result.get("deviceid"),
        }

    return {"code": code, "error": result.get("error", "login failed")}
