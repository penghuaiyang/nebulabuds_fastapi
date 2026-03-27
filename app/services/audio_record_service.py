"""Audio Record Service."""
import time
from typing import Any, Dict, List, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import AudioRecord

logger = log_util.get_logger("audio_record_service")

ONE_MONTH_MS = 30 * 24 * 3600 * 1000
PAGE_SIZE = 10
SPECIAL_CLIENT_ID = "PVMB8x1N"


class AudioRecordService:
    """音频记录服务类."""

    @classmethod
    async def get_records(
        cls,
        clientid: str,
        mac_addr: str,
        userid: int,
        page: int,
    ) -> Tuple[int, Dict[str, Any]]:
        """获取音频记录列表.

        Args:
            clientid: 客户端ID
            mac_addr: MAC地址
            userid: 用户ID
            page: 页码

        Returns:
            Tuple[code, data]
            - code=1: 成功
            - code=-1: 异常
        """
        try:
            if clientid != SPECIAL_CLIENT_ID:
                mac_check = await cls._check_mac_binding(clientid, mac_addr)
                if mac_check != 1:
                    return mac_check, {}

            current_time = time.time()
            one_month_ago = int((current_time * 1000) - ONE_MONTH_MS)
            offset = (page - 1) * PAGE_SIZE

            audio_records = await AudioRecord.filter(
                userid=userid, time__gte=one_month_ago
            ).order_by("-time").limit(PAGE_SIZE).offset(offset).all()

            records = []
            for record in audio_records:
                records.append(await record.to_dict())

            return 1, {"records": records}

        except Exception as exc:
            logger.exception(f"Get audio records failed: {exc}")
            return -1, {"error": str(exc)}

    @staticmethod
    async def _check_mac_binding(clientid: str, mac_addr: str) -> int:
        """检查 MAC 地址绑定状态.

        Returns:
            1: 绑定正常
            其他: 绑定异常
        """
        from app.models.models import UserMacBinding

        binding = await UserMacBinding.filter(
            clientid=clientid, mac=mac_addr, unbind_time=0
        ).first()

        if binding:
            return 1
        return -2
