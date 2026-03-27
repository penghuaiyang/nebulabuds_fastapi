"""Auth Token 签发/刷新处理器."""
from typing import Any

from fastapi import Header, Request

from app.common.schemas.auth_schema import AuthRequestSchema
from app.common.utils.blacklist_utils import is_blacklisted
from app.common.utils.jwt_utils import jwt_manager, no_auth_required
from app.common.utils.log_utils import log_util
from app.services.user_service import UserService

logger = log_util.get_logger("auth_handler")


async def _get_real_ip(request: Request) -> str:
    """获取真实 IP。"""
    return request.headers.get("X-Real-IP", request.client.host if request.client else "")


async def _check_user_device_match(userid: int, deviceid: str) -> tuple[bool, int, str]:
    """检查 userid 和 deviceid 是否仍然匹配。"""
    try:
        user_info = await UserService.get_user_by_userid(userid)
        if not user_info:
            return False, -27, "认证不通过 无法签发token"

        user_deviceid = user_info.get("deviceid", "")
        if user_deviceid != deviceid:
            return False, -27, "认证不通过 无法签发token"
        return True, 0, ""
    except Exception as exc:
        logger.error(f"Failed to check user device match: {exc}")
        return False, -1, str(exc)


@no_auth_required
async def auth(
    data: AuthRequestSchema,
    request: Request,
    refresh_token: str | None = Header(default=None, alias="Refresh-Token"),
) -> dict[str, Any]:
    """处理 Token 签发/刷新请求。"""
    real_ip = await _get_real_ip(request)

    if data.auth_type == "1":
        return await _handle_auth_issue(data.userid, data.deviceid, real_ip)
    if data.auth_type == "2":
        return await _handle_auth_refresh(refresh_token, real_ip)
    return {"code": -3, "message": f"无效的 auth_type: {data.auth_type}"}


async def _handle_auth_issue(
    userid: int | None,
    deviceid: str | None,
    real_ip: str,
) -> dict[str, Any]:
    """处理 Token 签发。"""
    if userid is None or not deviceid:
        return {"code": -2, "message": "userid and deviceid are required"}

    if await is_blacklisted(userid, deviceid):
        logger.warning(
            f"黑名单信息 userid: {userid} deviceid: {deviceid} ip_addr: {real_ip}"
        )
        return {"code": -26, "message": "接口火爆稍后尝试"}

    is_valid, error_code, error_msg = await _check_user_device_match(userid, deviceid)
    if not is_valid:
        return {"code": error_code, "message": error_msg}

    auth_data = {"userid": userid, "deviceid": deviceid}
    access_token = jwt_manager.create_access_token(auth_data)
    new_refresh_token = jwt_manager.create_refresh_token(auth_data)
    return {
        "code": 1,
        "message": "签发成功",
        "data": {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
        },
    }


async def _handle_auth_refresh(refresh_token: str | None, real_ip: str) -> dict[str, Any]:
    """处理 Token 刷新。"""
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

    try:
        userid = int(userid)
    except (TypeError, ValueError):
        return {"code": -7, "message": "Token payload 缺少必要字段"}

    if await is_blacklisted(userid, deviceid):
        logger.warning(
            f"黑名单信息 userid: {userid} deviceid: {deviceid} ip_addr: {real_ip}"
        )
        return {"code": -26, "message": "接口火爆稍后尝试"}

    is_valid, error_code, error_msg = await _check_user_device_match(userid, deviceid)
    if not is_valid:
        return {"code": error_code, "message": error_msg}

    auth_data = {"userid": userid, "deviceid": deviceid}
    access_token = jwt_manager.create_access_token(auth_data)
    new_refresh_token = jwt_manager.create_refresh_token(auth_data)
    return {
        "code": 1,
        "message": "刷新成功",
        "data": {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
        },
    }
