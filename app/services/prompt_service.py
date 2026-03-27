"""Prompt Service."""
import json
import os
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings
from app.common.utils.log_utils import log_util

logger = log_util.get_logger("prompt_service")

PROMPT_DIR = "/var/local/buds/prompts/"


class PromptService:
    """提示词服务类."""

    @classmethod
    async def get_prompt(
        cls,
        language_code: str,
    ) -> Tuple[int, Dict[str, Any]]:
        """获取提示词配置.

        Args:
            language_code: 语言代码

        Returns:
            Tuple[code, data]
        """
        try:
            prompt = await cls._load_prompt(language_code)
            prompt_version = settings.prompt_version

            return 1, {
                "prompt": prompt,
                "prompt_version": prompt_version,
            }

        except Exception as exc:
            logger.exception(f"Get prompt failed: {exc}")
            return -1, {"error": str(exc)}

    @classmethod
    async def _load_prompt(cls, language_code: str) -> Dict[str, Any]:
        """加载提示词文件."""
        ai_path = os.path.join(PROMPT_DIR, f"{language_code}.json")
        if not os.path.exists(ai_path):
            ai_path = os.path.join(PROMPT_DIR, "en-US.json")

        try:
            if os.path.exists(ai_path):
                with open(ai_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as exc:
            logger.warning(f"Failed to load prompt file: {exc}")

        return {}
