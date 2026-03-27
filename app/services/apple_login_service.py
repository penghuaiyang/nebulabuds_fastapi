"""Apple 登录服务."""
from typing import Tuple

import app.common.utils.apple_auth as AppleAuth
from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import User

logger = log_util.get_logger("apple_login_service")


class AppleLoginService:
    """Apple 登录服务类."""

    @staticmethod
    async def _get_redis():
        """获取 Redis 客户端."""
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @classmethod
    async def login(
        cls,
        userid: int,
        id_token: str,
    ) -> Tuple[int, dict]:
        """处理 Apple 登录.

        Args:
            userid: 用户ID
            id_token: Apple ID Token

        Returns:
            Tuple[code, data]
            - code=1: 登录成功
            - code=-1: 系统错误
        """
        try:
            # 验证 Apple Token
            sub = await AppleAuth.verify_and_decode_token(id_token)
            if not sub:
                return -1, {"error": "invalid apple token"}

            redis_client = await cls._get_redis()

            # 检查 Apple sub 是否已绑定用户
            old_userid = await redis_client.hget(RedisKeys.APPLE_SUB_DB, sub)

            if old_userid:
                target_userid = int(old_userid)
                user = await User.filter(userid=target_userid).first()
                if not user:
                    return -1, {"error": "user not found"}
                deviceid = user.deviceid
            else:
                # 获取当前用户信息
                user = await User.filter(userid=userid).first()
                if not user:
                    return -1, {"error": "user not found"}

                # TODO: 实现分支用户创建逻辑
                # if user.has_any_binding():
                #     branched_user_info = await user.create_sso_branch_user()
                #     target_userid = branched_user_info["userid"]
                #     deviceid = branched_user_info["deviceid"]
                # else:
                target_userid = userid
                deviceid = user.deviceid

                # 绑定 Apple ID
                await redis_client.hset(RedisKeys.APPLE_SUB_DB, sub, target_userid)

            # 更新用户 Apple ID
            await User.filter(userid=target_userid).update(appleid=sub)

            return 1, {"userid": target_userid, "deviceid": deviceid}

        except Exception as exc:
            logger.exception(f"Apple login error: {exc}")
            return -1, {"error": str(exc)}
