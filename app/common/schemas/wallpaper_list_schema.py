"""Wallpaper List Schema 定义."""
from pydantic import BaseModel, Field


class WallpaperListRequestSchema(BaseModel):
    """壁纸列表请求."""

    userid: int = Field(..., description="用户ID")
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页数量")
