"""Refresh Token 接口处理器."""
from typing import Any

from fastapi import Header, Request

from app.common.schemas.refresh_token_schema import RefreshTokenRequestSchema
from app.common.utils.jwt_utils import no_auth_required
from app.common.utils.log_utils import log_util
from app.services.refresh_token_service import RefreshTokenService

logger = log_util.get_logger("refresh_token_handler")


@no_auth_required
async def refresh_token(
    data: RefreshTokenRequestSchema,
    request: Request,
    refresh_token: str | None = Header(default=None, alias="Refresh-Token"),
) -> dict[str, Any]:
    """处理 Token 刷新请求."""
    if not refresh_token:
        return {"code": -4, "message": "Refresh-Token header is required"}

    code, result = await RefreshTokenService.refresh(refresh_token)

    if code == 1:
        return {
            "code": 1,
            "message": "ok",
            "token": result.get("access_token"),
            "token_type": result.get("token_type"),
        }
    return {"code": code, "message": result.get("error", "refresh failed")}
