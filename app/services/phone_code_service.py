"""手机验证码服务."""
import random
import time
from typing import Tuple

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.common.utils.ali_sms_utils import AliSMS
from app.models.models import SmsRecord

logger = log_util.get_logger("phone_code_service")

SMS_CODE_LENGTH = 4
SMS_CODE_EXPIRE_SECONDS = 1200  # 20分钟


class PhoneCodeService:
    """手机验证码服务类."""

    @staticmethod
    def _generate_code() -> str:
        """生成4位随机验证码."""
        return str(random.randint(1000, 9999))

    @staticmethod
    async def _get_redis():
        """获取 Redis 客户端."""
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @staticmethod
    def is_valid_phone(phone_no: str) -> bool:
        """验证手机号格式（中国大陆）."""
        import re
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone_no))

    @classmethod
    async def send_code(
        cls,
        clientid: str,
        userid: int,
        nation_code: str,
        phone_no: str,
    ) -> Tuple[int, str]:
        """发送手机验证码.

        Args:
            clientid: 客户端ID
            userid: 用户ID
            nation_code: 国家代码
            phone_no: 手机号

        Returns:
            Tuple[code, message]
            - code=1: 发送成功
            - code=-1: 不支持的国家
            - code=-2: 手机号格式错误
            - code=-3: 发送失败
        """
        # 验证手机号格式
        if not cls.is_valid_phone(phone_no):
            logger.warning(f"Invalid phone number: {phone_no}, userid: {userid}")
            return -2, "Invalid phone number"

        # 目前只支持中国大陆
        if nation_code != "86":
            return -1, "Not supported nation code"

        # 生成验证码
        code = cls._generate_code()

        # 发送短信
        success, message = await AliSMS.send_sms(phone_no, code)

        # 记录短信发送结果
        send_time = int(time.time() * 1000)
        await SmsRecord.create(
            clientCode=clientid,
            userid=userid,
            nationCode=nation_code,
            phoneNo=phone_no,
            content=code,
            result=success == 1,
            time=send_time,
        )

        if success == 1:
            # 验证码存入 Redis
            redis_client = await cls._get_redis()
            cache_key = RedisKeys.sms_code(phone_no)
            await redis_client.setex(cache_key, SMS_CODE_EXPIRE_SECONDS, code)
            logger.info(f"SMS code sent: phone={phone_no}, userid={userid}")
            return 1, "ok"

        return -3, message
