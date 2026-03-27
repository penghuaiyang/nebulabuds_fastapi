"""手机验证码登录服务."""
from typing import Optional, Tuple

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import User

logger = log_util.get_logger("phone_code_login_service")

# 测试用特殊手机号
TEST_PHONE = "123456"
DEV_PHONE_PREFIX = "nebula"


class PhoneCodeLoginService:
    """手机验证码登录服务类."""

    @staticmethod
    async def _get_redis():
        """获取 Redis 客户端."""
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @classmethod
    async def verify_code(cls, phone_no: str, code: str) -> bool:
        """验证验证码是否正确."""
        redis_client = await cls._get_redis()
        cache_key = RedisKeys.sms_code(phone_no)
        stored_code = await redis_client.get(cache_key)
        return stored_code == str(code)

    @classmethod
    async def login(
        cls,
        userid: int,
        clientid: str,
        phone_no: str,
        code: str,
    ) -> Tuple[int, dict]:
        """处理手机验证码登录.

        Args:
            userid: 用户ID
            clientid: 客户端ID
            phone_no: 手机号
            code: 验证码

        Returns:
            Tuple[code, data]
            - code=1: 登录成功
            - code=0: 验证码错误
            - code=-1: 用户不存在
            - code=-3: 系统错误
        """
        try:
            # 测试手机号直接通过
            if phone_no == TEST_PHONE:
                user = await User.filter(userid=10066502).first()
                if user:
                    return 1, {"userid": user.userid, "deviceid": user.deviceid}
                return -1, {"error": "user not found"}

            # nebula开头的手机号为开发测试用
            if phone_no.startswith(DEV_PHONE_PREFIX):
                try:
                    test_userid = int(phone_no[len(DEV_PHONE_PREFIX) :])
                    user = await User.filter(userid=test_userid).first()
                    if user:
                        return 1, {"userid": user.userid, "deviceid": user.deviceid}
                    return -1, {"error": "user not found"}
                except ValueError:
                    return -3, {"error": "invalid nebula phone format"}

            # 验证验证码
            if not await cls.verify_code(phone_no, code):
                logger.warning(f"Invalid code: phone={phone_no}, code={code}")
                return 0, {"code": 0}

            redis_client = await cls._get_redis()

            # 检查手机号是否已绑定其他用户
            phone_no_db = RedisKeys.PHONENO_DB if hasattr(RedisKeys, "PHONENO_DB") else "phone_no"
            old_userid = await redis_client.hget(phone_no_db, phone_no)

            user = await User.filter(userid=userid).first()
            if not user:
                return -1, {"error": "user not found"}

            deviceid = user.deviceid

            if not old_userid:
                # 手机号未绑定，绑定该手机号
                await redis_client.hset(phone_no_db, phone_no, userid)
                # 更新用户手机号
                await User.filter(userid=userid).update(phoneNo=phone_no)
                logger.info(f"Phone bound: userid={userid}, phone={phone_no}")
            else:
                # 手机号已绑定其他用户
                old_user = await User.filter(userid=int(old_userid)).first()
                if old_user:
                    deviceid = old_user.deviceid
                # 更新旧用户的手机号
                await User.filter(userid=int(old_userid)).update(phoneNo=phone_no)
                logger.info(f"Phone re-bound: old_userid={old_userid}, new_userid={userid}")

            return 1, {"userid": userid if not old_userid else int(old_userid), "deviceid": deviceid}

        except Exception as exc:
            logger.exception(f"Phone code login error: {exc}")
            return -3, {"error": str(exc)}
