"""Delete Record Schema 定义."""
from pydantic import BaseModel, Field


class DeleteRecordRequestSchema(BaseModel):
    """删除音频记录请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
    audioid: int = Field(..., description="音频记录ID")
    userid: int = Field(..., description="用户ID")
