"""总结服务."""
from typing import Tuple

from app.common.llm.model_client import qwen_model
from app.common.utils.log_utils import log_util

logger = log_util.get_logger("summary_service")

# palmzen 平台 clientid（不需要 MAC 验证）
PALMZEN_CLIENT_ID = "PVMB8x1N"

SUMMARY_SYSTEM_PROMPT = """Extract a summary of this text and display it as a 1,2,3 list. The language of the summary should be consistent with the content."""


class SummaryService:
    """总结服务类."""

    @classmethod
    async def summarize(
        cls,
        clientid: str,
        mac_addr: str,
        userid: int,
        word: str,
    ) -> Tuple[int, dict]:
        """处理内容总结请求.

        Args:
            clientid: 客户端ID
            mac_addr: MAC地址
            userid: 用户ID
            word: 待总结文本

        Returns:
            Tuple[code, data]
            - code=1: 总结成功
            - code=-1: 总结失败
            - code=-3: MAC验证失败
        """
        try:
            # palmzen 平台不需要 MAC 验证
            if clientid != PALMZEN_CLIENT_ID:
                # TODO: 需要实现 MAC 验证逻辑
                pass

            # 构建消息
            messages = [
                {"role": "user", "content": word},
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            ]

            # 调用 GPT-4o 进行总结
            # TODO: 实现具体的 GPT 调用逻辑
            # response = await gpt4o.async_openai_completion(messages)
            # if response.get("code") != 1:
            #     return response.get("code"), {"error": response, "code": response.get("code")}

            # 暂时返回原文作为占位
            return 1, {
                "summary": word,
                "code": 1,
            }

        except Exception as exc:
            logger.exception(f"Summary error: {exc}")
            return -1, {"error": str(exc), "code": -1}
