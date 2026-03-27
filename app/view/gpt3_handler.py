"""GPT3 AI对话接口处理器

支持 POST 请求，调用 GPT-4-mini Agent 进行 AI 对话。
"""
from typing import Any

from fastapi import Request

from app.common.schemas.gpt3_schema import Gpt3Schemas
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.gpt3_service import Gpt3Service

logger = log_util.get_logger("gpt3_handler")


@auth_required
async def gpt3(data: Gpt3Schemas, request: Request) -> dict[str, Any]:
    """GPT3 AI对话接口

    Args:
        data: 请求参数模型
        request: FastAPI 请求对象

    Returns:
        dict: 包含 code 和 message/error 的响应
    """
    try:
        params = {
            "userid": data.userid,
            "clientid": data.clientid,
            "macAddr": data.macAddr,
            "language": data.language or "",
            "requestFrom": data.requestFrom,
            "needTTS": data.needTTS,
            "word": data.word,
        }

        result = await Gpt3Service.gpt(params)
        return result

    except ValueError as exc:
        logger.warning(f"Gpt3 request validation error: {exc}")
        return {"code": -1, "error": str(exc)}
    except Exception as exc:
        logger.exception(f"Gpt3 request error: {exc}")
        return {"code": -1, "error": str(exc)}
