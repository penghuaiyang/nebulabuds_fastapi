"""Auth 相关 Schema 定义"""
from typing import Literal

from pydantic import BaseModel, Field

from app.common.schemas.base import BaseSchema


class AuthIssueSchema(BaseSchema):
    """auth_type=1: 签发 Token"""

    auth_type: Literal["1"] = Field(description="认证类型，1=签发Token")
    userid: int = Field(description="用户ID")
    deviceid: str = Field(min_length=1, max_length=64, description="设备ID")


class AuthRefreshSchema(BaseSchema):
    """auth_type=2: 刷新 Token"""

    auth_type: Literal["2"] = Field(description="认证类型，2=刷新Token")
