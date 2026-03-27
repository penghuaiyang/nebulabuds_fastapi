"""OTA Check Schema."""
from pydantic import BaseModel, Field, field_validator
import re


class OTARequestSchema(BaseModel):
    """OTA检查请求."""

    firmware_id: str = Field(..., min_length=1, max_length=256, description="固件ID")
    current_version: str = Field(..., description="当前版本")

    @field_validator("current_version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        pattern = r"^v?\d+\.\d+\.\d+$"
        if not re.match(pattern, v):
            raise ValueError("current_version format error, expected format: x.x.x or vx.x.x")
        if v.lower().startswith("v"):
            return v[1:]
        return v
