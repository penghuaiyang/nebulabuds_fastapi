"""Assistant Record Service."""
import json
import os
from typing import Any, Dict, List, Tuple

from app.common.utils.log_utils import log_util

logger = log_util.get_logger("assistant_record_service")

PROMPT_DIR = "/var/local/buds/prompts/"
DEFAULT_DICT_PATH = os.path.join(PROMPT_DIR, "en-US_dict.json")


class AssistantRecordService:
    """助手记录服务类."""

    @classmethod
    async def get_records(
        cls,
        clientid: str,
        userid: int,
        language_code: str,
    ) -> Tuple[int, Dict[str, Any]]:
        """获取助手记录列表.

        Args:
            clientid: 客户端ID
            userid: 用户ID
            language_code: 语言代码

        Returns:
            Tuple[code, data]
        """
        try:
            records = await cls._get_assistant_records(clientid, userid)
            assistant_dict = await cls._load_assistant_dict(language_code)

            assistant_records = []
            for record in records:
                if record in assistant_dict:
                    assistant_records.append(assistant_dict[record])

            return 1, {"assistantRecords": assistant_records}

        except Exception as exc:
            logger.exception(f"Get assistant records failed: {exc}")
            return -1, {"error": str(exc)}

    @staticmethod
    async def _get_assistant_records(clientid: str, userid: int) -> List[str]:
        """获取助手记录列表（从数据库或其他来源）."""
        return []

    @classmethod
    async def _load_assistant_dict(cls, language_code: str) -> Dict[str, str]:
        """加载助手记录字典."""
        dict_path = os.path.join(PROMPT_DIR, f"{language_code}_dict.json")
        if not os.path.exists(dict_path):
            dict_path = DEFAULT_DICT_PATH

        try:
            if os.path.exists(dict_path):
                with open(dict_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as exc:
            logger.warning(f"Failed to load assistant dict: {exc}")

        return {}
