"""Text2Img Schema 定义."""
from typing import Optional

from pydantic import BaseModel, Field


class Text2ImgRequestSchema(BaseModel):
    """文字生成图片请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
    userid: int = Field(..., description="用户ID")
    prompt: str = Field(..., description="生成提示词")
    size: Optional[int] = Field(default=0, description="图片尺寸: 0=正方形, 1=横屏, 2=竖屏")
