"""Prompt 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.prompt_schema import PromptRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.prompt_service import PromptService

logger = log_util.get_logger("prompt_handler")


@auth_required
@check_params
async def prompt(data: PromptRequestSchema, request: Request) -> dict[str, Any]:
    """处理提示词查询请求."""
    code, result = await PromptService.get_prompt(
        language_code=data.language_code,
    )

    return result
