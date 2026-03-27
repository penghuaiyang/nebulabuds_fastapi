"""BTBuds Schema 定义."""
from typing import Optional, List

from pydantic import BaseModel, Field


class BTBudsRequestSchema(BaseModel):
    """蓝牙耳机设备查询请求."""

    userid: Optional[int] = Field(default=None, description="用户ID")
    clientid: Optional[str] = Field(default=None, max_length=64, description="客户端ID")
    bt_name: Optional[List[str]] = Field(default=None, description="蓝牙名称列表")
    current_bt_name: Optional[str] = Field(default=None, max_length=64, description="当前蓝牙名称")
