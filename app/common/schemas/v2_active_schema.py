"""V2Active Schema 定义."""
from typing import Optional

from pydantic import BaseModel, Field


class V2ActiveRequestSchema(BaseModel):
    """V2 设备激活请求."""

    bt_name: str = Field(..., max_length=64, description="蓝牙设备名称")
    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
    userid: Optional[int] = Field(default=None, description="用户ID")
