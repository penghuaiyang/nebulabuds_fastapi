"""Music CDN Service."""
from typing import Any, Dict, Tuple

from app.common.utils.log_utils import log_util

logger = log_util.get_logger("music_cdn_service")

CDN_US = {
    "data_uri": "https://palmzencdn.azureedge.net/data/",
    "data_sp": "r&st=2024-08-09T06:54:58Z&se=2035-08-09T14:54:58Z&spr=https&sv=2022-11-02&sr=c&sig=zPcVor%2Fs1V%2F9QdOShQuUZ3xlaDOOyon9KxrZKRb6Tnk%3D",
    "mp3_uri": "https://palmzencdn.azureedge.net/mp3/",
    "mp3_sp": "r&st=2024-08-08T06:01:08Z&se=2034-08-08T14:01:08Z&spr=https&sv=2022-11-02&sr=c&sig=W4BhBFhmckDhyRM4S8Yjva8eK%2BkllR%2FCy6wVQT6i4k8%3D",
    "image_uri": "https://palmzencdn.azureedge.net/image/",
    "image_sp": "r&st=2024-08-08T07:24:18Z&se=2035-08-08T15:24:18Z&spr=https&sv=2022-11-02&sr=c&sig=V5OmYhwzB9S51Voyr2mvUv1JU2RQ%2FwsTLeVHMCWmj7o%3D"
}

CDN_CN = {
    "data_uri": "https://palmzencdn.azureedge.net/data/",
    "data_sp": "r&st=2024-08-09T06:54:58Z&se=2035-08-09T14:54:58Z&spr=https&sv=2022-11-02&sr=c&sig=zPcVor%2Fs1V%2F9QdOShQuUZ3xlaDOOyon9KxrZKRb6Tnk%3D",
    "mp3_uri": "https://nebulaeastasiacdn.azureedge.net/mp3/",
    "mp3_sp": "r&st=2024-08-09T10:53:03Z&se=2025-08-09T18:53:03Z&spr=https&sv=2022-11-02&sr=c&sig=cMBPDdXfe5HgGaPOd%2FNiL%2B7oJ3vwcpyTEWiG%2FZgRs1w%3D",
    "image_uri": "https://palmzencdn.azureedge.net/image/",
    "image_sp": "r&st=2024-08-08T07:24:18Z&se=2035-08-08T15:24:18Z&spr=https&sv=2022-11-02&sr=c&sig=V5OmYhwzB9S51Voyr2mvUv1JU2RQ%2FwsTLeVHMCWmj7o%3D"
}


class MusicCDNService:
    """音乐CDN服务类."""

    @classmethod
    async def get_cdn_config(
        cls,
        language_code: str,
    ) -> Tuple[int, Dict[str, Any]]:
        """获取CDN配置.

        Args:
            language_code: 语言代码

        Returns:
            Tuple[code, data]
        """
        if language_code.startswith("zh"):
            return 1, {"cdn": CDN_CN}
        return 1, {"cdn": CDN_US}
