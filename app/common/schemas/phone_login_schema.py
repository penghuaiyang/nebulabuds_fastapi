"""PhoneLogin Schema 定义."""
from pydantic import BaseModel, Field


class PhoneLoginRequestSchema(BaseModel):
    """手机号直接登录请求."""

    userid: int = Field(..., description="用户ID")
    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    phoneNo: str = Field(..., min_length=1, max_length=32, description="手机号")
