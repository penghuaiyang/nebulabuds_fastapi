"""EmailLogin 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.email_login_schema import EmailLoginRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import no_auth_required
from app.common.utils.log_utils import log_util
from app.services.email_login_service import EmailLoginService

logger = log_util.get_logger("email_login_handler")


@no_auth_required
@check_params
async def email_login(data: EmailLoginRequestSchema, request: Request) -> dict[str, Any]:
    """处理邮箱登录请求."""
    code, result = await EmailLoginService.login(
        email=data.email,
        code=data.code,
        userid=data.userid,
    )

    if code == 1:
        return {
            "code": 1,
            "userid": result.get("userid"),
            "deviceid": result.get("deviceid"),
        }

    if code == -4:
        return {"code": -4, "error": "code error"}

    return {"code": code, "error": result.get("error", "login failed")}
