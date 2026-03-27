"""Music Play Report Schema."""
from pydantic import BaseModel, Field


class MusicPlayReportRequestSchema(BaseModel):
    """音乐播放上报请求."""

    userid: int = Field(..., description="用户ID")
    music_id: int = Field(..., gt=0, description="音乐ID")
