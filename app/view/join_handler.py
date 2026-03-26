"""Join 接口处理器。"""
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.common.utils.join_utils import check, create_pass
from app.common.utils.jwt_utils import no_auth_required
from app.common.utils.log_utils import log_util
from app.services.user_service import UserService

logger = log_util.get_logger("join_handler")

JOIN_SIGNATURE_FIELDS = (
    "clientid",
    "deviceid",
    "platform",
    "nation",
    "localLanguage",
    "brand",
)
PARAMS_ERROR_RESPONSE = {"code": 0, "error": "params error"}


def _build_join_example(
    clientid: str,
    deviceid: str,
    platform: Optional[str],
    nation: Optional[str],
    local_language: Optional[str],
    brand: Optional[str],
) -> dict[str, Any]:
    """构造带签名的 Join 请求示例。"""
    payload = {
        "clientid": clientid,
        "deviceid": deviceid,
        "platform": platform,
        "nation": nation,
        "localLanguage": local_language,
        "brand": brand,
    }
    return create_pass(payload)


JOIN_REQUEST_EXAMPLES = [
    _build_join_example(
        clientid="PVMB8x1N",
        deviceid="UUID_DEVICE_001",
        platform="0",
        nation="CN",
        local_language="zh-CN",
        brand="Apple",
    ),
    _build_join_example(
        clientid="PVMB8x1N",
        deviceid="UUID_DEVICE_001",
        platform=None,
        nation=None,
        local_language=None,
        brand=None,
    ),
]


class JoinSchemas(BaseModel):
    """Join 请求模型。"""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={"examples": JOIN_REQUEST_EXAMPLES},
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
    platform: Optional[Literal["0", "1"]] = Field(
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




def _normalize_platform(value: Optional[str]) -> Optional[int]:
    """标准化平台字段。"""
    if value is None:
        return None
    return int(value)


@no_auth_required
async def join(data: JoinSchemas) -> dict[str, Any]:
    """处理用户注册/登录请求。"""
    params = data.model_dump(by_alias=True)
    if not check(params):
        logger.warning(
            "Join params error: "
            f"signature check failed for clientid={params.get('clientid')}, "
            f"deviceid={params.get('deviceid')}"
        )
        return PARAMS_ERROR_RESPONSE.copy()

    user_info = await UserService.join(
        clientid=data.clientid,
        deviceid=data.deviceid,
        platform=_normalize_platform(data.platform),
        nation=data.nation,
        localLanguage=data.localLanguage,
        brand=data.brand,
    )
    return {"code": 1, "userInfo": user_info}
