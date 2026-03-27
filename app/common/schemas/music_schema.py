"""Music List Schema 定义."""
from pydantic import BaseModel, Field


class MusicRequestSchema(BaseModel):
    """音乐列表请求."""

    language_code: str = Field(..., min_length=2, max_length=16, description="语言代码")
