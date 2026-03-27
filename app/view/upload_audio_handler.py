"""Upload Audio 接口处理器."""
from typing import Any, Optional

from fastapi import File, Form, Request, UploadFile

from app.common.utils.join_utils import check_params
from app.common.utils.jwt_utils import auth_required
from app.common.utils.log_utils import log_util
from app.services.upload_audio_service import UploadAudioService

logger = log_util.get_logger("upload_audio_handler")

ALLOWED_AUDIO_TYPES = {0, 1, 2, 3, 4}


@auth_required
async def upload_audio(
    clientid: str = Form(..., description="客户端ID"),
    userid: int = Form(..., description="用户ID"),
    macAddr: str = Form(..., description="MAC地址"),
    poi: Optional[str] = Form(None, description="位置信息"),
    content: str = Form(..., description="音频内容"),
    translate: str = Form(..., description="翻译内容"),
    duration: int = Form(..., description="音频时长(秒)"),
    phoneNo: Optional[str] = Form(None, description="电话号码"),
    audioType: int = Form(..., ge=0, le=4, description="音频类型"),
    pass_: str = Form(..., alias="pass", description="签名校验"),
    audio: UploadFile = File(..., description="音频文件"),
    request: Request = None,
) -> dict[str, Any]:
    """处理音频上传请求."""
    if audioType not in ALLOWED_AUDIO_TYPES:
        return {"error": "Invalid audio type", "code": -1}

    code, result = await UploadAudioService.upload_audio(
        clientid=clientid,
        userid=userid,
        mac_addr=macAddr,
        poi=poi,
        content=content,
        translate=translate,
        duration=duration,
        phone_no=phoneNo,
        audio_type=audioType,
        audio_file=audio,
    )

    return result
