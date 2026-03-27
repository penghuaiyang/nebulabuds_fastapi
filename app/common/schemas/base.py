"""基础 Schema 定义"""
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """带签名校验的基类 Schema

    所有需要签名校验的接口 Schema 都应继承此类
    """

    pass_: str = Field(
        ...,
        alias="pass",
        min_length=1,
        max_length=64,
        description="签名校验",
    )
