"""手机验证码发送接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.phone_code_schema import PhoneCodeRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import no_auth_required
from app.common.utils.log_utils import log_util
from app.services.phone_code_service import PhoneCodeService

logger = log_util.get_logger("phone_code_handler")


@no_auth_required
@check_params
async def phone_code(data: PhoneCodeRequestSchema, request: Request) -> dict[str, Any]:
    """处理发送手机验证码请求."""
    code, message = await PhoneCodeService.send_code(
        clientid=data.clientid,
        userid=data.userid,
        nation_code=data.nationCode,
        phone_no=data.phoneNo,
    )

    if code == 1:
        return {"code": 1, "message": "ok"}

    error_messages = {
        -1: "Not supported nation code",
        -2: "Invalid phone number",
        -3: "send sms error",
    }
    return {
        "code": code,
        "error": error_messages.get(code, message),
    }
