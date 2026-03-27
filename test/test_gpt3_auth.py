import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from loguru import logger

_original_logger_add = logger.add


def _safe_logger_add(*args, **kwargs):
    kwargs["enqueue"] = False
    return _original_logger_add(*args, **kwargs)


logger.add = _safe_logger_add

from app.common.schemas.auth_schema import AuthRequestSchema
from app.common.schemas.gpt3_schema import Gpt3Schemas
from app.common.utils.join_utils import create_pass
from app.view.auth_handler import auth
from app.view.gpt3_handler import gpt3


def _build_gpt3_data(userid: int) -> Gpt3Schemas:
    payload = create_pass(
        {
            "userid": userid,
            "clientid": "tx-11033",
            "macAddr": "AA:BB:CC",
            "language": "zh",
            "requestFrom": "app",
            "needTTS": 0,
            "word": "hello",
        }
    )
    return Gpt3Schemas(**payload)


class Gpt3HandlerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_gpt3_rejects_mismatched_userid(self) -> None:
        data = _build_gpt3_data(userid=10001)
        request = SimpleNamespace(state=SimpleNamespace(user_id=10002))

        with patch(
            "app.view.gpt3_handler.Gpt3Service.gpt",
            AsyncMock(return_value={"code": 1}),
        ) as gpt_mock:
            result = await gpt3(data, request)

        self.assertEqual(result["code"], -21)
        gpt_mock.assert_not_called()

    async def test_gpt3_uses_token_userid(self) -> None:
        data = _build_gpt3_data(userid=10001)
        request = SimpleNamespace(state=SimpleNamespace(user_id=10001))

        with patch(
            "app.view.gpt3_handler.Gpt3Service.gpt",
            AsyncMock(return_value={"code": 1}),
        ) as gpt_mock:
            result = await gpt3(data, request)

        self.assertEqual(result["code"], 1)
        gpt_mock.assert_awaited_once()
        self.assertEqual(gpt_mock.await_args.args[0]["userid"], 10001)


class AuthHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_auth_refresh_rechecks_device_binding(self) -> None:
        data = AuthRequestSchema(auth_type="2")
        request = SimpleNamespace(headers={}, client=None)

        with patch(
            "app.view.auth_handler.jwt_manager.verify_token",
            return_value={"type": "refresh", "userid": 10001, "deviceid": "device-a"},
        ):
            with patch(
                "app.view.auth_handler.is_blacklisted",
                AsyncMock(return_value=False),
            ):
                with patch(
                    "app.view.auth_handler._check_user_device_match",
                    AsyncMock(return_value=(False, -27, "认证不通过 无法签发token")),
                ):
                    result = await auth(data, request, "refresh-token")

        self.assertEqual(result["code"], -27)


if __name__ == "__main__":
    unittest.main()
