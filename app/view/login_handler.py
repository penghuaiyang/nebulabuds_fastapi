"""Login 接口处理器。"""
import time
from typing import Any

from pydantic import BaseModel, Field
from fastapi import Request

from app.common.schemas.base import BaseSchema
from app.common.utils.jwt_utils import no_auth_required
from app.common.utils.log_utils import log_util
from app.services.login_service import LoginService

logger = log_util.get_logger("login_handler")


class LoginSchemas(BaseSchema):
    """Login 请求模型（继承自 BaseSchema，包含签名字段）"""

    userid: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="用户ID",
    )
    clientid: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="客户端ID",
    )
    deviceid: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="设备ID",
    )


@no_auth_required
async def login(data: LoginSchemas, request: Request) -> dict[str, Any]:
    """处理用户登录请求。"""
    try:
        user_info = await LoginService.login(
            userid=data.userid,
            clientid=data.clientid,
            deviceid=data.deviceid,
        )
        # 兼容原接口格式：code=1 成功
        return {
            "code": 1,
            "userInfo": user_info,
            "sysTime": int(time.time()),
            "token": {
                "accessToken": "accessToken",
                "accessExpireTime": "accessExpireTime",
                "refreshToken": "refreshToken",
                "refreshExpireTime": "refreshExpireTime",
            },
        }
    except ValueError as exc:
        # 用户不存在
        logger.warning(f"Login failed: {exc}")
        return {"code": -3, "error": "user not exist"}
    except Exception as exc:
        logger.exception(f"Login error: {exc}")
        return {"code": -1, "error": str(exc)}
