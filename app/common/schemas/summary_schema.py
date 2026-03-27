"""Summary Schema 定义."""
from typing import Optional

from pydantic import BaseModel, Field


class SummaryRequestSchema(BaseModel):
    """总结请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
    userid: int = Field(..., description="用户ID")
    word: str = Field(..., description="待总结文本")
