"""Apple Pay 请求 Schema."""
from pydantic import BaseModel, Field


class ApplePayRequestSchema(BaseModel):
    """Apple Pay 请求参数."""
    userid: int = Field(..., description="用户ID")
    receipt_data: str = Field(..., description="Apple 支付收据数据")
