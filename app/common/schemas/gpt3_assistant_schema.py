"""GPT3Assistant Schema 定义."""
from typing import Optional

from pydantic import BaseModel, Field


class Gpt3AssistantRequestSchema(BaseModel):
    """GPT3 助手对话请求."""

    clientid: str = Field(..., min_length=1, max_length=64, description="客户端ID")
    macAddr: str = Field(..., min_length=1, max_length=64, description="MAC地址")
    userid: int = Field(..., description="用户ID")
    requestFrom: Optional[str] = Field(default="app", description="请求来源")
    assistanid: str = Field(..., description="助手ID")
    is_cn: Optional[int] = Field(default=1, description="是否中文: 1=是, 0=否")
    prompt: str = Field(..., description="系统提示词")
    languageCode: str = Field(..., max_length=16, description="语言代码")
    needTTS: Optional[int] = Field(default=0, description="是否需要TTS")
    word: str = Field(..., description="用户输入")
