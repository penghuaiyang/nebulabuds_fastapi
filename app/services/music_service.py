"""Music Service."""
import json
import os
from typing import Any, Dict, List, Tuple

from app.common.utils.log_utils import log_util

logger = log_util.get_logger("music_service")

MUSIC_DATA_DIR = "/var/local/music/music/"


class MusicService:
    """音乐服务类."""

    @classmethod
    async def get_music_list(
        cls,
        language_code: str,
    ) -> Tuple[int, Dict[str, Any]]:
        """获取音乐列表.

        Args:
            language_code: 语言代码

        Returns:
            Tuple[code, data]
        """
        try:
            music = await cls._load_music(language_code)
            return 1, {"music": music}

        except Exception as exc:
            logger.exception(f"Get music list failed: {exc}")
            return -1, {"error": str(exc)}

    @classmethod
    async def _load_music(cls, language_code: str) -> List[Dict[str, Any]]:
        """加载音乐列表文件."""
        mp3_path = os.path.join(MUSIC_DATA_DIR, f"data_{language_code}.json")

        try:
            if os.path.exists(mp3_path):
                with open(mp3_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as exc:
            logger.warning(f"Failed to load music file: {exc}")

        return []
