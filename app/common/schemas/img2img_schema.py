"""Img2Img Schema 定义."""
from pydantic import BaseModel, Field
from typing import Optional


class Img2ImgRequestSchema(BaseModel):
    """图片生成图片请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    userid: int = Field(..., description="用户ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
    prompt: str = Field(..., description="生成提示词")
    format: str = Field(default="jpeg", description="图片格式")
    pass_: str = Field(default=None, alias="pass", description="签名")
