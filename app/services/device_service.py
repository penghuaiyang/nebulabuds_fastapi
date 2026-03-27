"""设备信息更新服务."""
from typing import Tuple

from app.common.utils.log_utils import log_util
from app.models.models import User

logger = log_util.get_logger("device_service")


class DeviceService:
    """设备信息服务类."""

    @classmethod
    async def update_clientid_and_mac(
        cls,
        userid: int,
        clientid: str,
        mac_addr: str,
    ) -> Tuple[int, str]:
        """更新用户的客户端ID和MAC地址.

        Args:
            userid: 用户ID
            clientid: 客户端ID
            mac_addr: MAC地址

        Returns:
            Tuple[code, message]
        """
        try:
            await User.filter(userid=userid).update(
                clientCode=clientid,
                mac=mac_addr,
            )
            logger.info(f"Updated clientid and mac: userid={userid}, clientid={clientid}, mac={mac_addr}")
            return 1, "ok"
        except Exception as exc:
            logger.exception(f"Update clientid and mac failed: {exc}")
            return -1, str(exc)
