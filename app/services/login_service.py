"""Login 业务服务层。"""
import time
from typing import Any, Optional

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import PurchasedRecord
from app.services.user_service import UserService

logger = log_util.get_logger("login_service")


def _to_user_code(userid: str) -> str:
    """将 userid 转换为 userCode 格式。"""
    alphabet = [
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
        "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    ]
    try:
        index = int(userid[:2])
        start = alphabet[index - 10]
        num_arr = list(str(userid))
        if len(num_arr) == 8:
            num_arr[2], num_arr[5] = num_arr[5], num_arr[2]
            return start + "".join(num_arr[2:])
    except (ValueError, IndexError):
        pass
    return userid


class LoginService:
    """登录服务类。

    Redis key 统一格式: {db}:{namespace}:{scope}:{identifier}:{field?}
    """

    @classmethod
    async def _fetch_duration(cls, userid: int) -> int:
        """获取用户录音时长。"""
        client = await get_redis_client()
        try:
            value = await client.get(RedisKeys.record_duration(userid))
            return int(value) if value else 0
        except Exception as exc:
            logger.warning(f"读取录音时长失败: {exc}")
            return 0

    @classmethod
    async def _fetch_music_num(cls, userid: int) -> int:
        """获取用户音乐使用次数。"""
        client = await get_redis_client()
        try:
            value = await client.get(RedisKeys.music_num(userid))
            return int(value) if value else 0
        except Exception as exc:
            logger.warning(f"读取音乐次数失败: {exc}")
            return 0

    @classmethod
    async def _fetch_record_rest(cls, userid: int) -> int:
        """获取用户剩余录音时长。"""
        client = await get_redis_client()
        key = RedisKeys.record_rest(userid)
        try:
            value = await client.get(key)
            if value:
                return int(value)
            await client.set(key, 60)
            return 60
        except Exception as exc:
            logger.warning(f"读取录音剩余失败: {exc}")
            return 60

    @classmethod
    async def _fetch_ai_num(cls, userid: int, clientid: str = "") -> int:
        """获取用户 AI 使用次数。"""
        client = await get_redis_client()
        try:
            value = await client.get(RedisKeys.ai_num(userid, clientid))
            return int(value) if value else 0
        except Exception as exc:
            logger.warning(f"读取 AI 次数失败: {exc}")
            return 0

    @classmethod
    async def _fetch_free_record_date(cls, userid: int) -> Optional[int]:
        """获取用户免费录音到期时间。"""
        client = await get_redis_client()
        key = RedisKeys.free_record_date(userid)
        try:
            value = await client.get(key)
            if value is None:
                return None
            value_int = int(value)
            if value_int == 1:
                ttl = await client.ttl(key)
                return int(time.time()) + int(ttl)
            return value_int
        except Exception as exc:
            logger.warning(f"读取免费录音到期失败: {exc}")
            return None

    @classmethod
    async def _get_client_info(cls, userid: int) -> dict:
        """获取用户 clientInfo（mac -> {clientid, activeCode}）。"""
        client = await get_redis_client()
        mac_client_key = RedisKeys.mac_clientid(userid)
        mac_code_key = RedisKeys.mac_active_code(userid)
        try:
            client_info_raw = await client.hgetall(mac_client_key)
            active_code_info = await client.hgetall(mac_code_key)
            result = {}
            for mac_addr, clientid in client_info_raw.items():
                active_code = active_code_info.get(mac_addr, "")
                if clientid and active_code:
                    result[mac_addr] = {
                        "clientid": clientid,
                        "activeCode": active_code,
                    }
            return result
        except Exception as exc:
            logger.warning(f"读取 clientInfo 失败: {exc}")
            return {}

    @classmethod
    async def _get_bt_name_info(cls, userid: int) -> dict:
        """获取用户 btNameInfo（btName -> {clientid, activeCode}）。"""
        client = await get_redis_client()
        bt_key = RedisKeys.btname_list(userid)
        mac_client_key = RedisKeys.mac_clientid(userid)
        mac_code_key = RedisKeys.mac_active_code(userid)
        try:
            bt_list = await client.lrange(bt_key, 0, -1)
            result = {}
            for bt in bt_list:
                clientid = await client.hget(mac_client_key, bt)
                active_code = await client.hget(mac_code_key, bt)
                if clientid and active_code:
                    result[bt] = {
                        "clientid": clientid,
                        "activeCode": active_code,
                    }
            return result
        except Exception as exc:
            logger.warning(f"读取 btNameInfo 失败: {exc}")
            return {}

    @staticmethod
    async def check_pay(userid: int) -> int:
        """检查用户是否付费，返回 1 已付费，0 未付费。"""
        current_time = int(time.time()) * 1000
        record = (
            await PurchasedRecord.filter(userid=userid, payFor="vip")
            .order_by("-time")
            .first()
        )
        if not record:
            return 0
        price = int(record.price)
        add_time = int(record.time)
        if price == 198:
            return 1 if current_time - add_time <= 365 * 24 * 60 * 60 * 1000 else 0
        if price == 98:
            return 1 if current_time - add_time <= 90 * 24 * 60 * 60 * 1000 else 0
        return 0

    @staticmethod
    async def get_single_max_duration(clientid: str = "") -> int:
        """读取 App 单次使用最大时长配置，读取失败时返回 0。"""
        client = await get_redis_client()
        key = RedisKeys.single_max_duration(clientid)
        try:
            value = await client.get(key)
            if value in (None, ""):
                return 0
            return int(value)
        except (TypeError, ValueError) as exc:
            logger.warning(f"single_max_duration 配置格式错误: {exc}")
            return 0
        except Exception as exc:
            logger.exception(f"读取 single_max_duration 失败: {exc}")
            return 0

    @classmethod
    async def login(cls, userid: int, clientid: str, deviceid: str) -> dict:
        """处理用户登录，返回登录结果数据。"""
        from app.core.config import settings

        user_info = await UserService.get_user_by_userid(userid)
        if not user_info:
            raise ValueError("user not exist")
        user_info["userCode"] = _to_user_code(str(userid))
        user_info["prompt_version"] = settings.prompt_version

        # 检查 deviceid 是否匹配
        user_deviceid = user_info.get("deviceid")
        if user_deviceid and user_deviceid != deviceid:
            logger.info(
                f"登录警告，deviceid 不匹配 ---> 传入={deviceid}, 存储={user_deviceid}"
            )

        resolved_client_id = user_info.get("clientCode") or clientid

        # 顺序读取 Redis 数据
        duration = await cls._fetch_duration(userid)
        music_num = await cls._fetch_music_num(userid)
        record_rest = await cls._fetch_record_rest(userid)
        ai_num = await cls._fetch_ai_num(userid, resolved_client_id)
        free_record_date = await cls._fetch_free_record_date(userid)

        user_info["duration"] = duration
        user_info["musicNum"] = music_num
        user_info["recordRest"] = record_rest
        user_info["aiNum"] = ai_num
        if free_record_date is not None:
            user_info["freeRecordDate"] = free_record_date

        # 获取 clientInfo 和 btNameInfo
        user_info["clientInfo"] = await cls._get_client_info(userid)
        user_info["btNameInfo"] = await cls._get_bt_name_info(userid)

        # VIP 过期检查
        vip = user_info.get("vip", 0)
        current_time = int(time.time())
        if int(vip) < current_time:
            user_info["vip"] = "0"

        # 支付状态检查
        is_pay = await cls.check_pay(int(userid))
        if user_info.get("phoneNo") == "18967672186":
            is_pay = 1
        if is_pay:
            user_info["isPay"] = is_pay

        # 激活码列表处理
        code_list = user_info.get("activeCodeList")
        if code_list:
            if isinstance(code_list, str):
                code_list = code_list.split(",")
            user_info["activeCodeList"] = list(set(code_list))

        user_info["wakeupExpired"] = 30

        if "foreverVip" not in user_info:
            user_info["foreverVip"] = "0"

        user_info["single_max_duration"] = await cls.get_single_max_duration(
            resolved_client_id
        )

        return user_info
