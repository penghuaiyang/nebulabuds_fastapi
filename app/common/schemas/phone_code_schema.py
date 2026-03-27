"""Phone Code Schema 定义."""
from pydantic import BaseModel, Field
from typing import Literal


class PhoneCodeRequestSchema(BaseModel):
    """发送手机验证码请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    nationCode: str = Field(default="86", max_length=8, description="国家代码")
    userid: int = Field(..., description="用户ID")
    phoneNo: str = Field(..., min_length=11, max_length=16, description="手机号")
