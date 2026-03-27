"""Music Record Schema 定义."""
from pydantic import BaseModel, Field


class MusicRecordRequestSchema(BaseModel):
    """音乐记录请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    userid: int = Field(..., description="用户ID")
