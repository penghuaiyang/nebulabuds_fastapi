"""Music Categories List Service."""
from typing import Any, Dict, List, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import MusicCategory

logger = log_util.get_logger("music_categories_list_service")


class MusicCategoriesListService:
    """音乐分类列表服务类."""

    @classmethod
    async def get_categories_list(
        cls,
    ) -> Tuple[int, Dict[str, Any]]:
        """获取音乐分类列表.

        Returns:
            Tuple[code, data]
        """
        try:
            categories = await MusicCategory.filter(is_active=True).order_by("-sort_order", "-id").all()

            category_list = []
            for cat in categories:
                category_list.append(await cat.to_dict())

            return 1, {"categories": category_list}

        except Exception as exc:
            logger.exception(f"Get categories list failed: {exc}")
            return -1, {"error": str(exc)}
