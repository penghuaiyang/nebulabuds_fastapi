"""OTA Check Service."""
from packaging import version as pkg_version
from typing import Any, Dict, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import Firmware

logger = log_util.get_logger("ota_check_service")


class OTACheckService:
    """OTA检查服务类."""

    @classmethod
    async def check_update(
        cls,
        firmware_id: str,
        current_version: str,
    ) -> Tuple[int, Dict[str, Any]]:
        """检查固件更新.

        Args:
            firmware_id: 固件ID
            current_version: 当前版本

        Returns:
            Tuple[code, data]
            - code=1: 有更新
            - code=2: 无更新
            - code=-2: 固件不可用
            - code=-3: 版本格式错误
        """
        try:
            firmware = await Firmware.filter(
                firmware_id=firmware_id,
                is_active=True,
            ).first()

            if not firmware:
                return -2, {"error": "firmware not available"}

            if pkg_version.parse(current_version) < pkg_version.parse(firmware.version):
                return 1, {
                    "firmware_id": firmware.firmware_id,
                    "version": firmware.version,
                    "description": firmware.description,
                    "url": firmware.url,
                }

            return 2, {
                "latest_version": firmware.version,
            }

        except Exception as exc:
            logger.exception(f"OTA check failed: {exc}")
            return -1, {"error": str(exc)}
