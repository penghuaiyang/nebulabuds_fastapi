"""GPT3Assistant 接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.gpt3_assistant_schema import Gpt3AssistantRequestSchema
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.gpt3_assistant_service import Gpt3AssistantService

logger = log_util.get_logger("gpt3_assistant_handler")


@auth_required
@check_params
async def gpt3_assistant(data: Gpt3AssistantRequestSchema, request: Request) -> dict[str, Any]:
    """处理 GPT3 助手对话请求."""
    code, result = await Gpt3AssistantService.chat(
        userid=data.userid,
        clientid=data.clientid,
        mac_addr=data.macAddr,
        request_from=data.requestFrom or "app",
        assistanid=data.assistanid,
        is_cn=data.is_cn or 1,
        prompt=data.prompt,
        language_code=data.languageCode,
        need_tts=data.needTTS or 0,
        word=data.word,
    )

    if code == 1:
        return result

    return {"code": code, "error": result.get("error", "chat failed")}
