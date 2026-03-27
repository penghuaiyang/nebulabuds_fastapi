"""Refresh Token 服务."""
from datetime import timedelta
from typing import Tuple

from app.common.utils.jwt_utils import jwt_manager
from app.common.utils.blacklist_utils import is_blacklisted
from app.common.utils.log_utils import log_util
from app.services.user_service import UserService

logger = log_util.get_logger("refresh_token_service")


class RefreshTokenService:
    """Refresh Token 服务类."""

    @staticmethod
    async def refresh(refresh_token: str) -> Tuple[int, dict]:
        """刷新访问令牌.

        Args:
            refresh_token: 刷新令牌

        Returns:
            Tuple[code, data]
            - code=1: 刷新成功
            - code=-1: token无效
            - code=-2: token过期
            - code=-3: 其他错误
        """
        try:
            # 验证 refresh token
            payload = jwt_manager.verify_token(refresh_token)
            if not payload:
                return -1, {"error": "invalid token"}

            if payload.get("type") != "refresh":
                return -1, {"error": "not a refresh token"}

            userid = payload.get("userid")
            deviceid = payload.get("deviceid")

            if not userid or not deviceid:
                return -1, {"error": "invalid token payload"}

            # 检查黑名单
            if await is_blacklisted(int(userid), deviceid):
                logger.warning(f"Blacklisted user refresh: userid={userid}")
                return -3, {"error": "user is blacklisted"}

            # 验证用户和设备匹配
            user_info = await UserService.get_user_by_userid(int(userid))
            if not user_info:
                return -1, {"error": "user not found"}

            if user_info.get("deviceid") != deviceid:
                return -1, {"error": "deviceid mismatch"}

            # 生成新的 access token
            auth_data = {"userid": userid, "deviceid": deviceid}
            access_token = jwt_manager.create_access_token(auth_data)

            return 1, {
                "access_token": access_token,
                "token_type": "Bearer",
            }

        except Exception as exc:
            logger.exception(f"Refresh token error: {exc}")
            return -3, {"error": str(exc)}
