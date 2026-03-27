"""GPT3 请求模型"""
from typing import Optional

from pydantic import Field

from app.common.schemas.base import BaseSchema


class Gpt3Schemas(BaseSchema):
    """GPT3 AI对话请求模型"""

    userid: int = Field(..., description="用户ID")
    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
    language: Optional[str] = Field(None, max_length=16, description="语言")
    requestFrom: str = Field(..., description="请求来源")
    needTTS: int = Field(..., description="是否需要TTS: 0=不需要, 1=需要")
    word: str = Field(..., min_length=1, description="对话内容")
