"""WallpaperDeleteRequestSchema."""
from pydantic import BaseModel, Field


class WallpaperDeleteRequestSchema(BaseModel):
    """壁纸删除请求."""

    userid: int = Field(..., description="用户ID")
    wallpaperid: int = Field(..., description="壁纸ID")
