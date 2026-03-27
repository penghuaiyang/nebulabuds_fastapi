"""Google/X 订阅登录服务."""
from typing import Literal, Tuple

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import User

logger = log_util.get_logger("sub_login_service")

# subType 到 Redis key 的映射
SUB_TYPE_KEYS = {
    "google": RedisKeys.GOOGLE_SUB_DB,
    "x": RedisKeys.X_SUB_DB,
}


class SubLoginService:
    """Google/X 订阅登录服务类."""

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
        sub: str,
        userid: int,
        sub_type: Literal["google", "x"] = "google",
    ) -> Tuple[int, dict]:
        """处理 Google/X 订阅登录.

        Args:
            sub: 第三方 sub ID
            userid: 用户ID
            sub_type: 登录类型

        Returns:
            Tuple[code, data]
            - code=1: 登录成功
            - code=-4: subType 错误
            - code=-3: 系统错误
        """
        try:
            if sub_type not in SUB_TYPE_KEYS:
                return -4, {"error": "subType error"}

            redis_client = await cls._get_redis()
            redis_key = SUB_TYPE_KEYS[sub_type]

            # 检查 sub 是否已绑定用户
            old_userid = await redis_client.hget(redis_key, sub)

            if old_userid:
                target_userid = int(old_userid)
                user = await User.filter(userid=target_userid).first()
                if not user:
                    return -3, {"error": "user not found"}
                deviceid = user.deviceid
                # 更新登录信息
                await User.filter(userid=target_userid).update(loginName=sub)
            else:
                # 获取当前用户信息
                user = await User.filter(userid=userid).first()
                if not user:
                    return -3, {"error": "user not found"}

                # TODO: 实现分支用户创建逻辑
                # if user.has_any_binding():
                #     branched_user_info = await user.create_sso_branch_user()
                #     target_userid = branched_user_info["userid"]
                #     deviceid = branched_user_info["deviceid"]
                # else:
                target_userid = userid
                deviceid = user.deviceid

                # 绑定 sub
                await redis_client.hset(redis_key, sub, target_userid)
                await User.filter(userid=userid).update(loginName=sub)

            logger.info(f"Sub login success: sub_type={sub_type}, target_userid={target_userid}")
            return 1, {"userid": target_userid, "deviceid": deviceid}

        except Exception as exc:
            logger.exception(f"Sub login error: {exc}")
            return -3, {"error": str(exc)}
