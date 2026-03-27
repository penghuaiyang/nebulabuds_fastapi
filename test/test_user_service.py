import json
import time
import unittest
from unittest.mock import AsyncMock, patch

from loguru import logger

_original_logger_add = logger.add


def _safe_logger_add(*args, **kwargs):
    kwargs["enqueue"] = False
    return _original_logger_add(*args, **kwargs)


logger.add = _safe_logger_add

from app.db.redis_keys import RedisKeys
from app.services.login_service import LoginService
from app.services.user_service import UserService


class FakeUser:
    """用于用户缓存测试的轻量用户对象。"""

    def __init__(self, userid: int, deviceid: str, client_code: str = "demo") -> None:
        self.userid = userid
        self.deviceid = deviceid
        self.clientCode = client_code
        self.avartar = "1.jpg"
        self.macInfo = None
        self.phoneNo = None
        self.appleid = None
        self.platForm = 0
        self.nation = "CN"
        self.localLanguage = "zh"
        self.brand = "Nebula"
        self.nickName = "Tester001"
        self.email = "0"
        self.vip = 1710003600
        self.time = 1710000000000

    async def to_dict(self) -> dict:
        return {
            "id": 1,
            "userid": self.userid,
            "deviceid": self.deviceid,
            "avatar": self.avartar,
            "clientCode": self.clientCode,
            "macInfo": self.macInfo,
            "phoneNo": self.phoneNo,
            "appleid": self.appleid,
            "platForm": self.platForm,
            "nation": self.nation,
            "localLanguage": self.localLanguage,
            "brand": self.brand,
            "nickName": self.nickName,
            "email": self.email,
            "time": self.time,
        }


class UserServiceTestCase(unittest.IsolatedAsyncioTestCase):
    """用户服务缓存测试。"""

    async def test_get_user_by_userid_returns_cache_when_hit(self) -> None:
        cached_user = {
            "userid": 10001,
            "deviceid": "device-a",
            "clientCode": "demo",
            "vip": 1710003600,
        }
        redis_client = AsyncMock()
        redis_client.get = AsyncMock(return_value=json.dumps(cached_user))

        with patch.object(UserService, "_get_redis", AsyncMock(return_value=redis_client)):
            with patch.object(
                UserService,
                "_query_user_by_userid",
                AsyncMock(),
            ) as query_mock:
                user_info = await UserService.get_user_by_userid(10001)

        self.assertEqual(user_info, cached_user)
        query_mock.assert_not_called()
        redis_client.get.assert_awaited_once_with(RedisKeys.user_profile(10001))

    async def test_get_user_by_userid_backfills_cache_on_miss(self) -> None:
        fake_user = FakeUser(userid=10002, deviceid="device-b")
        redis_client = AsyncMock()
        redis_client.get = AsyncMock(return_value=None)
        redis_client.setex = AsyncMock()

        with patch.object(UserService, "_get_redis", AsyncMock(return_value=redis_client)):
            with patch.object(
                UserService,
                "_query_user_by_userid",
                AsyncMock(return_value=fake_user),
            ):
                user_info = await UserService.get_user_by_userid(10002)

        self.assertEqual(user_info["userid"], 10002)
        self.assertEqual(redis_client.setex.await_count, 2)
        expected_payload = json.dumps((await fake_user.to_dict()) | {"vip": fake_user.vip})
        redis_client.setex.assert_any_await(
            RedisKeys.device_user_id("device-b"),
            86400,
            expected_payload,
        )
        redis_client.setex.assert_any_await(
            RedisKeys.user_profile(10002),
            86400,
            expected_payload,
        )

    async def test_get_user_by_userid_falls_back_to_db_when_redis_unavailable(self) -> None:
        fake_user = FakeUser(userid=10003, deviceid="device-c")

        with patch.object(
            UserService,
            "_get_redis",
            AsyncMock(side_effect=RuntimeError("redis unavailable")),
        ):
            with patch.object(
                UserService,
                "_query_user_by_userid",
                AsyncMock(return_value=fake_user),
            ):
                user_info = await UserService.get_user_by_userid(10003)

        self.assertEqual(user_info["userid"], 10003)
        self.assertEqual(user_info["deviceid"], "device-c")

    async def test_get_user_by_userid_returns_none_when_user_missing(self) -> None:
        redis_client = AsyncMock()
        redis_client.get = AsyncMock(return_value=None)

        with patch.object(UserService, "_get_redis", AsyncMock(return_value=redis_client)):
            with patch.object(
                UserService,
                "_query_user_by_userid",
                AsyncMock(return_value=None),
            ):
                user_info = await UserService.get_user_by_userid(10004)

        self.assertIsNone(user_info)

    async def test_get_user_by_userid_refills_incomplete_cache(self) -> None:
        fake_user = FakeUser(userid=10007, deviceid="device-f")
        redis_client = AsyncMock()
        redis_client.get = AsyncMock(
            return_value=json.dumps(
                {"userid": 10007, "deviceid": "device-f", "clientCode": "demo"}
            )
        )
        redis_client.setex = AsyncMock()

        with patch.object(UserService, "_get_redis", AsyncMock(return_value=redis_client)):
            with patch.object(
                UserService,
                "_query_user_by_userid",
                AsyncMock(return_value=fake_user),
            ) as query_mock:
                user_info = await UserService.get_user_by_userid(10007)

        self.assertEqual(user_info["vip"], fake_user.vip)
        query_mock.assert_awaited_once_with(10007)
        self.assertEqual(redis_client.setex.await_count, 2)

    async def test_is_vip_uses_cached_user_info(self) -> None:
        with patch.object(
            UserService,
            "get_user_by_userid",
            AsyncMock(return_value={"userid": 10008, "vip": int(time.time()) + 60}),
        ):
            self.assertTrue(await UserService.is_vip(10008))

    async def test_invalidate_user_cache_deletes_both_keys(self) -> None:
        redis_client = AsyncMock()
        redis_client.delete = AsyncMock()

        with patch.object(UserService, "_get_redis", AsyncMock(return_value=redis_client)):
            await UserService.invalidate_user_cache("device-d", 10005)

        redis_client.delete.assert_awaited_once_with(
            RedisKeys.device_user_id("device-d"),
            RedisKeys.user_profile(10005),
        )


class LoginServiceTestCase(unittest.IsolatedAsyncioTestCase):
    """登录服务测试。"""

    async def test_login_raises_when_user_missing(self) -> None:
        with patch.object(
            UserService,
            "get_user_by_userid",
            AsyncMock(return_value=None),
        ):
            with self.assertRaisesRegex(ValueError, "user not exist"):
                await LoginService.login(10006, "demo", "device-e")


if __name__ == "__main__":
    unittest.main()
