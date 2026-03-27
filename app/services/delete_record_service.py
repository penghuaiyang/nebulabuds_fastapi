"""Delete Record Service."""
from typing import Any, Dict, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import AudioRecord

logger = log_util.get_logger("delete_record_service")

SPECIAL_CLIENT_ID = "PVMB8x1N"


class DeleteRecordService:
    """删除音频记录服务类."""

    @classmethod
    async def delete_audio_record(
        cls,
        clientid: str,
        mac_addr: str,
        audioid: int,
        userid: int,
    ) -> Tuple[int, Dict[str, Any]]:
        """删除音频记录.

        Args:
            clientid: 客户端ID
            mac_addr: MAC地址
            audioid: 音频记录ID
            userid: 用户ID

        Returns:
            Tuple[code, data]
        """
        try:
            if clientid != SPECIAL_CLIENT_ID:
                mac_check = await cls._check_mac_binding(clientid, mac_addr)
                if mac_check != 1:
                    return mac_check, {}

            audio_record = await AudioRecord.filter(id=audioid, userid=userid).first()
            if audio_record:
                await audio_record.delete()

            return 1, {}

        except Exception as exc:
            logger.exception(f"Delete audio record failed: {exc}")
            return -1, {"error": str(exc)}

    @staticmethod
    async def _check_mac_binding(clientid: str, mac_addr: str) -> int:
        """检查 MAC 地址绑定状态."""
        from app.models.models import UserMacBinding

        binding = await UserMacBinding.filter(
            clientid=clientid, mac=mac_addr, unbind_time=0
        ).first()

        if binding:
            return 1
        return -2
