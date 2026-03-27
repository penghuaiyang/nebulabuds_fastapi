"""AppleLogin Schema 定义."""
from pydantic import BaseModel, Field


class AppleLoginRequestSchema(BaseModel):
    """Apple登录请求."""

    userid: int = Field(..., description="用户ID")
    id_token: str = Field(..., description="Apple ID Token")
