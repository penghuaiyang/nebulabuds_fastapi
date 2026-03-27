"""Phone Code Login Schema 定义."""
from pydantic import BaseModel, Field


class PhoneCodeLoginRequestSchema(BaseModel):
    """手机验证码登录请求."""

    userid: int = Field(..., description="用户ID")
    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    phoneNo: str = Field(..., min_length=1, max_length=16, description="手机号")
    phoneCode: str = Field(..., min_length=4, max_length=8, description="验证码")
