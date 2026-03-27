"""GPT-4-mini Agent 工具封装

从旧项目 nebulabuds/api/dify/gpt4mini_tools.py 迁移
"""
import httpx

from app.common.utils.log_utils import log_util

logger = log_util.get_logger("gpt4mini_utils")

API_URL = "http://124.222.17.175:81/v1/chat-messages"
API_KEY = "app-vrTjNr3ww6BN2Dj4JhncsacQ"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


async def gpt41mini_agent(query: str, user: str, conversation_id: str, language: str) -> tuple[str, str]:
    """异步调用 GPT-4-mini 接口，返回 answer 和 conversation_id。

    Args:
        query: 用户输入的查询内容
        user: 用户标识
        conversation_id: 会话ID，用于保持上下文
        language: 语言设置

    Returns:
        tuple: (回答内容, 新的会话ID)
    """
    payload = {
        "inputs": {
            "language": language,
        },
        "query": query,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": user,
    }

    try:
        async with httpx.AsyncClient(timeout=50) as client:
            resp = await client.post(API_URL, json=payload, headers=HEADERS)
            data = resp.json()
            answer = data.get("answer", "No answer provided")
            conv_id = data.get("conversation_id", "")
            return answer, conv_id
    except httpx.TimeoutException:
        logger.error("GPT-4-mini request timeout")
        return "请求超时，请稍后重试", ""
    except httpx.HTTPError as exc:
        logger.exception(f"GPT-4-mini request failed: {exc}")
        return f"服务暂时不可用: {str(exc)}", ""
    except Exception as exc:
        logger.exception(f"Unexpected error in gpt41mini_agent: {exc}")
        return "发生未知错误", ""
