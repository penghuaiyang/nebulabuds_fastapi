"""Upload Audio Schema 定义."""
from typing import Optional

from pydantic import BaseModel, Field


class UploadAudioRequestSchema(BaseModel):
    """音频上传请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    userid: int = Field(..., description="用户ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
    poi: Optional[str] = Field(default=None, max_length=128, description="位置信息")
    content: str = Field(..., description="音频内容")
    translate: str = Field(..., description="翻译内容")
    duration: int = Field(..., ge=0, description="音频时长(秒)")
    phoneNo: Optional[str] = Field(default=None, max_length=32, description="电话号码")
    audioType: int = Field(..., ge=0, le=4, description="音频类型: 0=电话录音,1=手机音视频,2=现场录音,3=同声传译,4=面对面翻译")
