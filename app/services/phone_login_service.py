"""手机号直接登录服务."""
from typing import Tuple

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import User

logger = log_util.get_logger("phone_login_service")


class PhoneLoginService:
    """手机号直接登录服务类."""

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
        clientid: str,
        phone_no: str,
    ) -> Tuple[int, dict]:
        """处理手机号直接登录.

        Args:
            userid: 用户ID
            clientid: 客户端ID
            phone_no: 手机号

        Returns:
            Tuple[code, data]
            - code=1: 登录成功
            - code=0: 参数错误
            - code=-3: 系统错误
        """
        try:
            redis_client = await cls._get_redis()

            # 检查手机号是否已绑定其他用户
            old_userid = await redis_client.hget(RedisKeys.PHONENO_DB, phone_no)

            if not old_userid:
                # 手机号未绑定，绑定该手机号
                await redis_client.hset(RedisKeys.PHONENO_DB, phone_no, userid)
                await User.filter(userid=userid).update(phoneNo=phone_no)
                logger.info(f"Phone bound: userid={userid}, phone={phone_no}")
                return 1, {"userid": userid}

            return 1, {"userid": int(old_userid)}

        except Exception as exc:
            logger.exception(f"Phone login error: {exc}")
            return -3, {"error": str(exc)}
