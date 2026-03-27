"""Weather Info Schema."""
from pydantic import BaseModel, Field, field_validator
import re


class WeatherInfoRequestSchema(BaseModel):
    """天气信息请求."""

    lat: str = Field(..., description="纬度")
    lng: str = Field(..., description="经度")
    time: str = Field(..., description="时间 YYYYMMDDhh")

    @field_validator("lat", "lng")
    @classmethod
    def validate_lat_lng(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("lat/lng must be a string")
        if not v.lstrip("-").isdigit():
            raise ValueError("lat/lng must be a numeric string")
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("time must be in format YYYYMMDDhh (10 digits)")
        return v
