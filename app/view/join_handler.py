"""Join 接口处理器。"""
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field
from fastapi import Request

from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import no_auth_required
from app.common.utils.log_utils import log_util
from app.services.user_service import UserService

logger = log_util.get_logger("join_handler")
PARAMS_ERROR_RESPONSE = {"code": 0, "error": "params error"}


class JoinSchemas(BaseModel):
    """Join 请求模型。"""

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
    platform: Optional[Literal[0, 1]] = Field(
        None,
        description="平台: 0=ios, 1=android",
    )
    nation: Optional[str] = Field(
        None,
        max_length=32,
        description="国家代码",
    )
    localLanguage: Optional[str] = Field(
        None,
        max_length=32,
        description="本地语言",
    )
    brand: Optional[str] = Field(
        None,
        max_length=32,
        description="手机品牌",
    )
    pass_: str = Field(
        ...,
        alias="pass",
        min_length=1,
        max_length=64,
        description="签名校验",
    )


@no_auth_required
@check_params
async def join(data: JoinSchemas, request: Request) -> dict[str, Any]:
    """处理用户注册/登录请求。"""

    user_info = await UserService.join(
        clientid=data.clientid,
        deviceid=data.deviceid,
        platform=data.platform,
        nation=data.nation,
        localLanguage=data.localLanguage,
        brand=data.brand,
    )
    return {"code": 1, "userInfo": user_info}
