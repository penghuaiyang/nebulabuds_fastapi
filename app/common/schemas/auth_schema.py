"""Auth schema definitions."""
from typing import Literal

from pydantic import BaseModel, Field


class AuthRequestSchema(BaseModel):
    """Auth token issue or refresh request body."""

    auth_type: Literal["1", "2"] = Field(description="认证类型")
    userid: int | None = Field(default=None, description="用户ID，仅 auth_type=1 必填")
    deviceid: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description="设备ID，仅 auth_type=1 必填",
    )
