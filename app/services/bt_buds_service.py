"""蓝牙耳机设备查询服务."""
from typing import Any, Dict, List, Optional, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import Buds, BudsBrand

logger = log_util.get_logger("bt_buds_service")

# 特殊品牌ID列表
SIN_BRAND_IDS = [248, 463, 464, 493]


class BTBudsService:
    """蓝牙耳机设备查询服务类."""

    @classmethod
    async def query_buds(
        cls,
        userid: Optional[int],
        clientid: Optional[str],
        bt_names: Optional[List[str]] = None,
        current_bt_name: Optional[str] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        """查询蓝牙耳机设备信息.

        Args:
            userid: 用户ID
            clientid: 客户端ID
            bt_names: 蓝牙名称列表
            current_bt_name: 当前蓝牙名称

        Returns:
            Tuple[code, data]
        """
        try:
            # 如果有 current_bt_name，优先查询当前设备
            if current_bt_name:
                current_obj = await Buds.filter(blName__contains=current_bt_name).first()
                if current_obj and current_obj.brandId in SIN_BRAND_IDS:
                    return 1, {
                        "code": 1,
                        "buds": await cls._buds_to_dict(current_obj),
                    }

            # 如果没有 bt_names，返回空
            if not bt_names:
                return 1, {"code": 1, "buds": {}}

            # 获取品牌ID列表
            if clientid and clientid != "guest":
                brand_ids = await BudsBrand.filter(clientId=clientid).values_list("id", flat=True)
            else:
                brand_ids = []

            buds_info = {}
            for bt_name in bt_names:
                if brand_ids:
                    buds_obj = await Buds.filter(
                        blName__contains=bt_name, brandId__in=brand_ids
                    ).first()
                else:
                    buds_obj = await Buds.filter(blName__contains=bt_name).first()

                if buds_obj:
                    buds_info[bt_name] = await cls._buds_to_dict(buds_obj)

            return 1, {"code": 1, "buds": buds_info}

        except Exception as exc:
            logger.exception(f"Query buds failed: {exc}")
            return -1, {"code": -1, "error": str(exc)}

    @staticmethod
    async def _buds_to_dict(buds: Buds) -> dict:
        """将 Buds 模型转换为字典."""
        return {
            "id": buds.id,
            "brandId": buds.brandId,
            "name": buds.name,
            "image": buds.image,
            "introduction": buds.introduction,
            "blName": buds.blName,
            "ifScreen": buds.ifScreen,
            "connectType": buds.connectType,
            "deviceType": buds.deviceType,
            "wallName": buds.wallName,
            "time": buds.time,
        }
