"""UpdateClientidAndMac Schema 定义."""
from pydantic import BaseModel, Field


class UpdateClientidAndMacRequestSchema(BaseModel):
    """更新客户端ID和MAC请求."""

    userid: int = Field(..., description="用户ID")
    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
