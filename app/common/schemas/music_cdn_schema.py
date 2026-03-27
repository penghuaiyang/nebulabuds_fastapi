"""Music CDN Schema."""
from pydantic import BaseModel, Field


class MusicCDNRequestSchema(BaseModel):
    """音乐CDN配置请求."""

    language_code: str = Field(..., min_length=2, max_length=16, description="语言代码")
