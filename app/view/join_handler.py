from typing import Optional

from app.common.utils.jwt_utils import no_auth_required
from pydantic import BaseModel, Field
from fastapi import Request


class JoinSchemas(BaseModel):
    deviceid: Optional[int] = Field(None, description="设备id")
    platform: Optional[str] = Field(None, description="平台", max_length=32)
    nation: Optional[str] = Field(None, description="国家代码", max_length=32)
    localLanguage: Optional[str] = Field(None, description="本地语言", max_length=32)
    brand: Optional[str] = Field(None, description="品牌", max_length=32)


@no_auth_required
async def join(data: JoinSchemas, request: Request):
    pass
