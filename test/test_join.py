"""Join 接口回归测试。"""
import unittest
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from tortoise.exceptions import IntegrityError

from app.common.utils.join_utils import create_pass
from app.router.router import router
from app.services.user_service import UserService
from app.view.join_handler import JOIN_SIGNATURE_FIELDS


def build_join_payload(**overrides: Any) -> dict[str, Any]:
    """构造符合旧签名规则的 Join 请求。"""
    payload = {
        field: overrides.get(field)
        for field in JOIN_SIGNATURE_FIELDS
    }
    payload["clientid"] = overrides.get("clientid", "PVMB8x1N")
    payload["deviceid"] = overrides.get("deviceid", "UUID_DEVICE_001")
    return create_pass(payload)


def create_test_app() -> FastAPI:
    """创建最小测试应用。"""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


class FakeUser:
    """测试用用户对象。"""

    def __init__(self, user_info: dict[str, Any]):
        self._user_info = user_info
        self.userid = user_info["userid"]
        self.deviceid = user_info["deviceid"]

    async def to_dict(self) -> dict[str, Any]:
        """返回用户字典。"""
        return self._user_info


class JoinHandlerTests(unittest.IsolatedAsyncioTestCase):
    """Join 接口测试。"""

    async def asyncSetUp(self) -> None:
        """初始化测试客户端。"""
        self.client = AsyncClient(
            transport=ASGITransport(app=create_test_app()),
            base_url="http://testserver",
        )

    async def asyncTearDown(self) -> None:
        """关闭测试客户端。"""
        await self.client.aclose()

    async def test_join_success_returns_legacy_payload(self) -> None:
        """首登成功时返回旧响应结构。"""
        user_info = {
            "id": 1,
            "userid": 10000000,
            "deviceid": "UUID_DEVICE_001",
            "clientCode": "PVMB8x1N",
            "macInfo": None,
            "phoneNo": None,
            "appleid": None,
            "platForm": 0,
            "nation": "CN",
            "localLanguage": "zh-CN",
            "brand": "Apple",
            "nickName": "HappyUser123",
            "email": "0",
            "time": 1711440000000,
        }
        payload = build_join_payload(
            platform="0",
            nation="CN",
            localLanguage="zh-CN",
            brand="Apple",
        )

        with patch(
            "app.view.join_handler.UserService.join",
            new=AsyncMock(return_value=user_info),
        ) as join_mock:
            response = await self.client.post("/api/v1/join/", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": 1, "userInfo": user_info})
        join_mock.assert_awaited_once_with(
            clientid="PVMB8x1N",
            deviceid="UUID_DEVICE_001",
            platform=0,
            nation="CN",
            localLanguage="zh-CN",
            brand="Apple",
        )

    async def test_join_accepts_pass_alias_payload(self) -> None:
        """pass 字段按旧别名参与签名校验。"""
        payload = build_join_payload()

        with patch(
            "app.view.join_handler.UserService.join",
            new=AsyncMock(return_value={"userid": 10000000}),
        ):
            response = await self.client.post("/api/v1/join/", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": 1, "userInfo": {"userid": 10000000}})

    async def test_join_invalid_params_return_legacy_error(self) -> None:
        """保护场景统一返回旧式参数错误。"""
        invalid_payloads = {
            "missing_pass": {k: v for k, v in build_join_payload().items() if k != "pass"},
            "empty_clientid": build_join_payload(clientid=""),
            "empty_deviceid": build_join_payload(deviceid=""),
            "invalid_platform": build_join_payload(platform="2"),
        }

        for case_name, payload in invalid_payloads.items():
            with self.subTest(case_name=case_name):
                response = await self.client.post("/api/v1/join/", json=payload)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"code": 0, "error": "params error"})

    def test_join_openapi_schema_contains_pass_field(self) -> None:
        """OpenAPI 中保留 Join 字段和旧签名字段。"""
        schema = create_test_app().openapi()
        request_schema = schema["paths"]["/api/v1/join/"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"]

        self.assertIn("pass", request_schema["properties"])
        self.assertIn("clientid", request_schema["required"])
        self.assertIn("deviceid", request_schema["required"])
        self.assertIn("pass", request_schema["required"])


class UserServiceJoinTests(unittest.IsolatedAsyncioTestCase):
    """UserService.join 测试。"""

    async def test_join_returns_cached_user(self) -> None:
        """缓存命中时直接返回用户信息。"""
        cached_user = {"userid": 10000000, "deviceid": "UUID_DEVICE_001"}

        with patch.object(
            UserService,
            "get_user_cache",
            new=AsyncMock(return_value=cached_user),
        ), patch("app.services.user_service.User.filter") as filter_mock:
            result = await UserService.join(
                clientid="PVMB8x1N",
                deviceid="UUID_DEVICE_001",
                platform=0,
                nation="CN",
                localLanguage="zh-CN",
                brand="Apple",
            )

        self.assertEqual(result, cached_user)
        filter_mock.assert_not_called()

    async def test_join_returns_existing_user_from_db(self) -> None:
        """缓存未命中但数据库命中时返回相同用户信息。"""
        user_info = {
            "userid": 10000000,
            "deviceid": "UUID_DEVICE_001",
            "clientCode": "PVMB8x1N",
        }
        fake_user = FakeUser(user_info)
        query = MagicMock()
        query.first = AsyncMock(return_value=fake_user)

        with patch.object(
            UserService,
            "get_user_cache",
            new=AsyncMock(return_value=None),
        ), patch.object(
            UserService,
            "set_user_cache",
            new=AsyncMock(),
        ) as set_cache_mock, patch(
            "app.services.user_service.User.filter",
            return_value=query,
        ):
            result = await UserService.join(
                clientid="PVMB8x1N",
                deviceid="UUID_DEVICE_001",
                platform=0,
                nation="CN",
                localLanguage="zh-CN",
                brand="Apple",
            )

        self.assertEqual(result, user_info)
        set_cache_mock.assert_awaited_once_with(fake_user)

    async def test_join_falls_back_after_integrity_error(self) -> None:
        """并发创建冲突时回退查询已存在用户。"""
        user_info = {
            "userid": 10000000,
            "deviceid": "UUID_DEVICE_001",
            "clientCode": "PVMB8x1N",
        }
        fake_user = FakeUser(user_info)

        empty_query = MagicMock()
        empty_query.first = AsyncMock(return_value=None)
        existing_query = MagicMock()
        existing_query.first = AsyncMock(return_value=fake_user)

        with patch.object(
            UserService,
            "get_user_cache",
            new=AsyncMock(return_value=None),
        ), patch.object(
            UserService,
            "allocate_userid",
            new=AsyncMock(return_value=10000000),
        ), patch.object(
            UserService,
            "set_user_cache",
            new=AsyncMock(),
        ) as set_cache_mock, patch(
            "app.services.user_service.User.filter",
            side_effect=[empty_query, existing_query],
        ), patch(
            "app.services.user_service.User.create",
            new=AsyncMock(side_effect=IntegrityError("duplicate deviceid")),
        ):
            result = await UserService.join(
                clientid="PVMB8x1N",
                deviceid="UUID_DEVICE_001",
                platform=0,
                nation="CN",
                localLanguage="zh-CN",
                brand="Apple",
            )

        self.assertEqual(result, user_info)
        set_cache_mock.assert_awaited_once_with(fake_user)


if __name__ == "__main__":
    unittest.main()
