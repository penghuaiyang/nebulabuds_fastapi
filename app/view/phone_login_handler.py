"""PhoneLogin 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.phone_login_schema import PhoneLoginRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.phone_login_service import PhoneLoginService

logger = log_util.get_logger("phone_login_handler")


@auth_required
@check_params
async def phone_login(data: PhoneLoginRequestSchema, request: Request) -> dict[str, Any]:
    """处理手机号直接登录请求."""
    code, result = await PhoneLoginService.login(
        userid=data.userid,
        clientid=data.clientid,
        phone_no=data.phoneNo,
    )

    if code == 1:
        return {
            "code": 1,
            "userid": result.get("userid"),
            "deviceid": result.get("deviceid"),
        }

    return {"code": code, "error": result.get("error", "login failed")}
