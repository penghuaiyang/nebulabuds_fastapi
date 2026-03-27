"""Upload Wallpaper Schema 定义."""
from typing import Optional

from pydantic import BaseModel, Field


class UploadWallpaperRequestSchema(BaseModel):
    """壁纸上传请求."""

    userid: int = Field(..., description="用户ID")
