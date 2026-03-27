"""手机验证码登录接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.phone_code_login_schema import PhoneCodeLoginRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import no_auth_required
from app.common.utils.log_utils import log_util
from app.services.phone_code_login_service import PhoneCodeLoginService

logger = log_util.get_logger("phone_code_login_handler")


@no_auth_required
@check_params
async def phone_code_login(data: PhoneCodeLoginRequestSchema, request: Request) -> dict[str, Any]:
    """处理手机验证码登录请求."""
    code, result = await PhoneCodeLoginService.login(
        userid=data.userid,
        clientid=data.clientid,
        phone_no=data.phoneNo,
        code=data.phoneCode,
    )

    if code == 1:
        return {
            "code": 1,
            "userid": result.get("userid"),
            "deviceid": result.get("deviceid"),
        }

    if code == 0:
        return {"code": 0, "message": "验证码错误"}

    return {
        "code": code,
        "error": result.get("error", "login failed"),
    }
