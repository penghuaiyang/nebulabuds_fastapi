"""Music Favorite Schema."""
from pydantic import BaseModel, Field


class MusicFavoriteRequestSchema(BaseModel):
    """音乐收藏请求."""

    userid: int = Field(..., description="用户ID")
    music_id: int = Field(..., gt=0, description="音乐ID")
    action: str = Field(..., pattern=r"^(add|remove)$", description="操作: add=收藏, remove=取消")
