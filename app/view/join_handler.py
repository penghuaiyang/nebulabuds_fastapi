"""Join 接口处理器。"""
from collections.abc import Mapping
from typing import Any, Optional

from fastapi import Body
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
JOIN_FIELD_LIMITS = {
    "clientid": 64,
    "deviceid": 64,
    "nation": 32,
    "localLanguage": 32,
    "brand": 32,
}
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
    """Join 请求文档模型。"""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={"examples": JOIN_REQUEST_EXAMPLES},
    )

    clientid: str = Field(..., description="客户端ID")
    deviceid: str = Field(..., description="设备ID")
    platform: Optional[str] = Field(None, description="平台: 0=ios, 1=android")
    nation: Optional[str] = Field(None, description="国家代码")
    localLanguage: Optional[str] = Field(None, description="本地语言")
    brand: Optional[str] = Field(None, description="手机品牌")
    pass_: str = Field(..., alias="pass", description="签名校验")


JOIN_ROUTE_OPENAPI_EXTRA = {
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": JoinSchemas.model_json_schema(by_alias=True),
            }
        },
    }
}
JOIN_ROUTE_RESPONSES = {
    200: {
        "description": "Join 接口响应",
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "登录成功",
                        "value": {
                            "code": 1,
                            "userInfo": {
                                "id": 1,
                                "userid": 10000000,
                                "deviceid": "UUID_DEVICE_001",
                                "clientCode": "PVMB8x1N",
                                "macInfo": None,
                                "phoneNo": None,
                                "appleid": None,
                                "platForm": 0,
                                "nation": "CN",
                                "localLanguage": "zh-CN",
                                "brand": "Apple",
                                "nickName": "HappyUser123",
                                "email": "0",
                                "time": 1711440000000,
                            },
                        },
                    },
                    "params_error": {
                        "summary": "参数或签名错误",
                        "value": PARAMS_ERROR_RESPONSE,
                    },
                }
            }
        },
    }
}


def _build_signature_params(raw_data: Mapping[str, Any]) -> dict[str, Any]:
    """按旧接口顺序构造签名参数。"""
    params = {field: raw_data.get(field) for field in JOIN_SIGNATURE_FIELDS}
    params["pass"] = raw_data.get("pass")
    return params


def _is_valid_required_text(value: Any, max_length: int) -> bool:
    """校验必填字符串字段。"""
    return isinstance(value, str) and value != "" and len(value) <= max_length


def _is_valid_optional_text(value: Any, max_length: int) -> bool:
    """校验可选字符串字段。"""
    return value is None or (isinstance(value, str) and len(value) <= max_length)


def _is_valid_platform(value: Any) -> bool:
    """校验平台字段。"""
    if value in (None, ""):
        return True
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value in (0, 1)
    if isinstance(value, str):
        return value in {"0", "1"}
    return False


def _validate_join_payload(raw_data: Any) -> Optional[str]:
    """返回 Join 请求参数错误原因。"""
    if not isinstance(raw_data, dict):
        return "request body is not a json object"

    if not _is_valid_required_text(raw_data.get("clientid"), JOIN_FIELD_LIMITS["clientid"]):
        return "invalid clientid"
    if not _is_valid_required_text(raw_data.get("deviceid"), JOIN_FIELD_LIMITS["deviceid"]):
        return "invalid deviceid"
    if not _is_valid_required_text(raw_data.get("pass"), 64):
        return "invalid pass"
    if not _is_valid_platform(raw_data.get("platform")):
        return "invalid platform"
    if not _is_valid_optional_text(raw_data.get("nation"), JOIN_FIELD_LIMITS["nation"]):
        return "invalid nation"
    if not _is_valid_optional_text(
        raw_data.get("localLanguage"), JOIN_FIELD_LIMITS["localLanguage"]
    ):
        return "invalid localLanguage"
    if not _is_valid_optional_text(raw_data.get("brand"), JOIN_FIELD_LIMITS["brand"]):
        return "invalid brand"
    return None


def _normalize_platform(value: Any) -> Optional[int]:
    """标准化平台字段。"""
    if value in (None, ""):
        return None
    return int(value)


def _params_error(reason: str) -> dict[str, Any]:
    """返回旧式参数错误响应。"""
    logger.warning(f"Join params error: {reason}")
    return PARAMS_ERROR_RESPONSE.copy()


@no_auth_required
async def join(
    data: Any = Body(default=None),
) -> dict[str, Any]:
    """处理用户注册/登录请求。"""
    validation_error = _validate_join_payload(data)
    if validation_error:
        return _params_error(validation_error)

    signature_params = _build_signature_params(data)
    if not check(signature_params):
        clientid = signature_params.get("clientid")
        deviceid = signature_params.get("deviceid")
        return _params_error(
            f"signature check failed for clientid={clientid}, deviceid={deviceid}"
        )

    user_info = await UserService.join(
        clientid=str(data["clientid"]),
        deviceid=str(data["deviceid"]),
        platform=_normalize_platform(data.get("platform")),
        nation=data.get("nation"),
        localLanguage=data.get("localLanguage"),
        brand=data.get("brand"),
    )
    return {"code": 1, "userInfo": user_info}
