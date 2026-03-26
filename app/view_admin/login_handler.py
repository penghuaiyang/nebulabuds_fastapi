from pydantic import Field, BaseModel
from fastapi import Request

from app.common.utils.jwt_utils import no_auth_required


class LoginSchemas(BaseModel):
    username: str = Field(description="用户名")
    password: str = Field(description="密码")


@no_auth_required
async def admin_login(data: LoginSchemas, request: Request):
    pass
