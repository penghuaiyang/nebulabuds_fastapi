"""Music Favorite List Schema."""
from pydantic import BaseModel, Field


class MusicFavoriteListRequestSchema(BaseModel):
    """音乐收藏列表请求."""

    userid: int = Field(..., description="用户ID")
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页数量")
