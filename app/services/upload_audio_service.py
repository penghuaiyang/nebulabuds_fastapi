"""Upload Audio Service."""
import os
import time
import random
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from fastapi import UploadFile

from app.common.utils.log_utils import log_util
from app.models.models import AudioRecord

logger = log_util.get_logger("upload_audio_service")

UPLOAD_PATH = "/var/local/buds/audio/"
ALLOWED_AUDIO_TYPES = {0, 1, 2, 3, 4}


class UploadAudioService:
    """音频上传服务类."""

    @classmethod
    async def upload_audio(
        cls,
        clientid: str,
        userid: int,
        mac_addr: str,
        poi: Optional[str],
        content: str,
        translate: str,
        duration: int,
        phone_no: Optional[str],
        audio_type: int,
        audio_file: UploadFile,
    ) -> Tuple[int, Dict[str, Any]]:
        """上传音频文件并创建记录.

        Args:
            clientid: 客户端ID
            userid: 用户ID
            mac_addr: MAC地址
            poi: 位置信息
            content: 音频内容
            translate: 翻译内容
            duration: 音频时长（秒）
            phone_no: 电话号码
            audio_type: 音频类型
            audio_file: 音频文件

        Returns:
            Tuple[code, data]
        """
        try:
            if audio_type not in ALLOWED_AUDIO_TYPES:
                return -1, {"error": "Invalid audio type"}

            file_ext = os.path.splitext(audio_file.filename)[1] if audio_file.filename else ".mp3"
            fname = f"{random.randint(0, 2 ** 32 - 1)}{file_ext}"

            now = datetime.now()
            formatted_date = now.strftime("%Y-%m-%d")
            audio_path = os.path.join(UPLOAD_PATH, formatted_date, fname)

            os.makedirs(os.path.dirname(audio_path), exist_ok=True)

            content_bytes = await audio_file.read()
            with open(audio_path, 'wb') as fh:
                fh.write(content_bytes)

            path = audio_path.replace('/buds', '')

            audio_record_obj = await AudioRecord.create(
                clientCode=clientid,
                userid=str(userid),
                poi=poi,
                path=path,
                content=content,
                translate=translate,
                duration=duration,
                phoneNo=phone_no,
                audioType=audio_type,
                time=int(time.time() * 1000)
            )

            pk = audio_record_obj.id

            return 1, {"code": 1, "id": pk}

        except Exception as exc:
            logger.exception(f"Upload audio failed: {exc}")
            return -1, {"error": str(exc)}
