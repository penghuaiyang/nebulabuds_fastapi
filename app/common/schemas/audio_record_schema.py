"""Audio Record Schema 定义."""
from typing import Optional

from pydantic import BaseModel, Field


class AudioRecordRequestSchema(BaseModel):
    """音频记录查询请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
    userid: int = Field(..., description="用户ID")
    page: int = Field(..., ge=1, description="页码")
