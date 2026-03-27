"""GPT3 AI对话接口处理器."""
from typing import Any

from fastapi import Request

from app.common.schemas.gpt3_schema import Gpt3Schemas
from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.gpt3_service import Gpt3Service

logger = log_util.get_logger("gpt3_handler")


@auth_required
@check_params
async def gpt3(data: Gpt3Schemas, request: Request) -> dict[str, Any]:
    """处理 GPT3 AI 对话请求。"""
    try:
        token_userid = int(request.state.user_id)
        if data.userid != token_userid:
            logger.warning(
                "Gpt3 token userid mismatch: "
                f"token_userid={token_userid}, body_userid={data.userid}"
            )
            return {
                "code": -21,
                "message": "认证失败",
                "data": {"detail": "userid does not match token"},
            }

        params = {
            "userid": token_userid,
            "clientid": data.clientid,
            "macAddr": data.macAddr,
            "language": data.language or "",
            "requestFrom": data.requestFrom,
            "needTTS": data.needTTS,
            "word": data.word,
        }
        return await Gpt3Service.gpt(params)
    except ValueError as exc:
        logger.warning(f"Gpt3 request validation error: {exc}")
        return {"code": -1, "error": str(exc)}
    except Exception as exc:
        logger.exception(f"Gpt3 request error: {exc}")
        return {"code": -1, "error": str(exc)}
