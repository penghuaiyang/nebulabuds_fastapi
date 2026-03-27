"""Assistant Record Schema 定义."""
from typing import Optional

from pydantic import BaseModel, Field


class AssistantRecordRequestSchema(BaseModel):
    """助手记录查询请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    userid: int = Field(..., description="用户ID")
    languageCode: str = Field(..., min_length=2, max_length=16, description="语言代码")
