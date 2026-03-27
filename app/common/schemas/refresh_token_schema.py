"""Refresh Token Schema 定义."""
from pydantic import BaseModel, Field
from typing import Literal


class RefreshTokenRequestSchema(BaseModel):
    """刷新Token请求."""

    pass  # 不需要请求体，token 从 header 获取
