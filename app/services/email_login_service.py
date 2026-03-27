"""邮箱登录服务."""
from typing import Tuple

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import User

logger = log_util.get_logger("email_login_service")

# 管理员测试邮箱
ADMIN_EMAIL = "g3230069@gmail.com"
ADMIN_CODE = "123321"


class EmailLoginService:
    """邮箱登录服务类."""

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
        email: str,
        code: str,
        userid: int,
    ) -> Tuple[int, dict]:
        """处理邮箱登录.

        Args:
            email: 邮箱地址
            code: 验证码
            userid: 用户ID

        Returns:
            Tuple[code, data]
            - code=1: 登录成功
            - code=-4: 验证码错误
            - code=0: 参数错误
            - code=-1: 系统错误
        """
        try:
            redis_client = await cls._get_redis()

            # 验证验证码
            cache_key = RedisKeys.email_code(email)
            stored_code = await redis_client.get(cache_key)

            # 管理员测试账号直接通过
            if email == ADMIN_EMAIL and code == ADMIN_CODE:
                pass
            elif str(code) != str(stored_code):
                logger.warning(f"Email login code mismatch: email={email}")
                return -4, {"error": "code error"}

            # 查询用户
            user = await User.filter(userid=userid).first()
            if not user:
                return -1, {"error": "user not found"}

            deviceid = user.deviceid

            # 检查邮箱是否已绑定其他用户
            old_userid = await redis_client.hget(RedisKeys.EMAIL_DB, email)
            if old_userid:
                target_userid = int(old_userid)
                target_user = await User.filter(userid=target_userid).first()
                if target_user:
                    deviceid = target_user.deviceid
                await User.filter(userid=target_userid).update(email=email)
            else:
                target_userid = userid
                await redis_client.hset(RedisKeys.EMAIL_DB, email, userid)
                await User.filter(userid=userid).update(email=email)

            # 删除验证码
            await redis_client.delete(cache_key)

            return 1, {"userid": target_userid, "deviceid": deviceid}

        except Exception as exc:
            logger.exception(f"Email login error: {exc}")
            return -1, {"error": str(exc)}
