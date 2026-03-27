"""Record Duration Schema 定义."""
from typing import Optional

from pydantic import BaseModel, Field


class RecordDurationRequestSchema(BaseModel):
    """录音时长记录请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    userid: int = Field(..., description="用户ID")
    duration: int = Field(..., ge=0, description="录音时长(秒)")
    activeCode: Optional[str] = Field(default=None, description="激活码")
    durationType: Optional[int] = Field(default=0, description="时长类型: 1=现场录音, 2=同声传译, 3=面对面翻译")
    isTRTC: Optional[int] = Field(default=0, ge=0, le=1, description="是否音视频通话")
