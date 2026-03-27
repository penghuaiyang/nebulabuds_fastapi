"""SubLogin Schema 定义."""
from pydantic import BaseModel, Field
from typing import Literal


class SubLoginRequestSchema(BaseModel):
    """Google/X 订阅登录请求."""

    sub: str = Field(..., description="第三方 sub ID")
    userid: int = Field(..., description="用户ID")
    subType: Literal["google", "x"] = Field(default="google", description="登录类型")
