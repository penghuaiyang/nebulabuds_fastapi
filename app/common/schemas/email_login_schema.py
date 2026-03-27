"""EmailLogin Schema 定义."""
from pydantic import BaseModel, Field


class EmailLoginRequestSchema(BaseModel):
    """邮箱登录请求."""

    email: str = Field(..., max_length=64, description="邮箱地址")
    code: str = Field(..., min_length=4, max_length=8, description="验证码")
    userid: int = Field(..., description="用户ID")
