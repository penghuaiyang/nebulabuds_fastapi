"""Auth Token 签发/刷新处理器"""
from typing import Any, Literal, Union

from fastapi import Request, Header
from pydantic import BaseModel, Field

from app.common.utils.jwt_utils import jwt_manager, no_auth_required
from app.common.utils.blacklist_utils import is_blacklisted
from app.db.redis import get_redis_client
from app.common.utils.log_utils import log_util
from app.services.user_service import UserService

logger = log_util.get_logger("auth_handler")


class AuthIssueRequest(BaseModel):
    """auth_type=1: 签发 Token 请求"""
    auth_type: Literal["1"] = Field(description="认证类型，1=签发Token")
    userid: int = Field(description="用户ID")
    deviceid: str = Field(min_length=1, max_length=64, description="设备ID")


class AuthRefreshRequest(BaseModel):
    """auth_type=2: 刷新 Token 请求"""
    auth_type: Literal["2"] = Field(description="认证类型，2=刷新Token")


async def _get_real_ip(request: Request) -> str:
    """获取真实IP"""
    return request.headers.get("X-Real-IP", request.client.host if request.client else "")


async def _check_user_device_match(userid: int, deviceid: str) -> tuple[bool, int, str]:
    """检查 userid 和 deviceid 是否匹配

    Returns:
        (is_valid, error_code, error_message)
    """
    try:
        user_info = await UserService.get_user_by_userid(userid)
        user_deviceid = user_info.get("deviceid", "")
        if user_deviceid != deviceid:
            return False, -27, "认证不通过 无法签发token"
        return True, 0, ""
    except Exception as e:
        logger.error(f"Failed to check user device match: {e}")
        return False, -1, str(e)


@no_auth_required
async def auth(request: Request) -> dict[str, Any]:
    """处理 Token 签发/刷新请求

    auth_type=1: 签发 access_token 和 refresh_token
    auth_type=2: 刷新 access_token
    """
    try:
        body = await request.json()
    except Exception:
        return {"code": -1, "message": "无效的请求体"}

    auth_type = body.get("auth_type")
    if not auth_type:
        return {"code": -2, "message": "auth_type is required"}

    real_ip = await _get_real_ip(request)

    if auth_type == "1":
        return await _handle_auth_issue(body, real_ip)
    elif auth_type == "2":
        refresh_token = request.headers.get("Refresh-Token")
        return await _handle_auth_refresh(refresh_token, real_ip)
    else:
        return {"code": -3, "message": f"无效的 auth_type: {auth_type}"}


async def _handle_auth_issue(data: dict, real_ip: str) -> dict[str, Any]:
    """处理 Token 签发"""
    userid = data.get("userid")
    deviceid = data.get("deviceid")

    if not userid or not deviceid:
        return {"code": -2, "message": "userid and deviceid are required"}

    userid = int(userid)

    if await is_blacklisted(userid, deviceid):
        logger.warning(f"黑名单信息 userid: {userid} deviceid: {deviceid} ip_addr: {real_ip}")
        return {"code": -26, "message": "接口火爆稍后尝试"}

    is_valid, error_code, error_msg = await _check_user_device_match(userid, deviceid)
    if not is_valid:
        return {"code": error_code, "message": error_msg}

    auth_data = {"userid": userid, "deviceid": deviceid}
    access_token = jwt_manager.create_access_token(auth_data)
    refresh_token = jwt_manager.create_refresh_token(auth_data)

    return {
        "code": 1,
        "message": "签发成功",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


async def _handle_auth_refresh(refresh_token: str | None, real_ip: str) -> dict[str, Any]:
    """处理 Token 刷新"""
    if not refresh_token:
        return {"code": -4, "message": "Refresh-Token header is required"}

    payload = jwt_manager.verify_token(refresh_token)
    if not payload:
        return {"code": -5, "message": "无效的 Refresh-Token"}

    if payload.get("type") != "refresh":
        return {"code": -6, "message": "Token 类型不正确，需要 refresh 类型"}

    userid = payload.get("userid")
    deviceid = payload.get("deviceid")

    if not userid or not deviceid:
        return {"code": -7, "message": "Token payload 缺少必要字段"}

    if await is_blacklisted(userid, deviceid):
        logger.warning(f"黑名单信息 userid: {userid} deviceid: {deviceid} ip_addr: {real_ip}")
        return {"code": -26, "message": "接口火爆稍后尝试"}

    auth_data = {"userid": userid, "deviceid": deviceid}
    access_token = jwt_manager.create_access_token(auth_data)
    new_refresh_token = jwt_manager.create_refresh_token(auth_data)

    return {
        "code": 1,
        "message": "刷新成功",
        "access_token": access_token,
        "refresh_token": new_refresh_token,
    }
