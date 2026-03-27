"""Router for all API endpoints."""
from fastapi import APIRouter

from app.view.gpt3_handler import gpt3
from app.view.join_handler import join
from app.view.login_handler import login
from app.view.auth_handler import auth
from app.view.refresh_token_handler import refresh_token
from app.view.phone_code_handler import phone_code
from app.view.phone_code_login_handler import phone_code_login
from app.view.v2_active_handler import v2_active
from app.view.update_clientid_mac_handler import update_clientid_mac
from app.view.bt_buds_handler import bt_buds
from app.view.translate_handler import translate
from app.view.summary_handler import summary
from app.view.text2img_handler import text2img
from app.view.gpt3_assistant_handler import gpt3_assistant
from app.view.phone_login_handler import phone_login
from app.view.email_login_handler import email_login
from app.view.apple_login_handler import apple_login
from app.view.sub_login_handler import sub_login
from app.view.active_handler import active
from app.view.img2img_handler import img2img
from app.view.audio_record_handler import audio_record
from app.view.assistant_record_handler import assistant_record
from app.view.music_record_handler import music_record
from app.view.record_duration_handler import record_duration
from app.view.delete_record_handler import delete_record
from app.view.prompt_handler import prompt
from app.view.music_handler import music
from app.view.wallpaper_list_handler import wallpaper_list
from app.view.upload_audio_handler import upload_audio
from app.view.upload_wallpaper_handler import upload_wallpaper
from app.view.wallpaper_delete_handler import wallpaper_delete
from app.view.weather_info_handler import weather_info
from app.view.music_favorite_handler import music_favorite
from app.view.music_favorite_list_handler import music_favorite_list
from app.view.music_categories_list_handler import music_categories_list
from app.view.music_cdn_handler import music_cdn
from app.view.music_play_report_handler import music_play_report
from app.view.ota_check_handler import ota_check


router = APIRouter()

router.add_api_route(
    path="/gpt3/",
    endpoint=gpt3,
    methods=["POST"],
    summary="GPT3 AI 对话",
    tags=["ai"],
)

router.add_api_route(
    path="/join/",
    endpoint=join,
    methods=["POST"],
    summary="Join 用户登录/注册",
    tags=["auth"],
)

router.add_api_route(
    path="/login/",
    endpoint=login,
    methods=["POST"],
    summary="Login 用户登录",
    tags=["auth"],
)

router.add_api_route(
    path="/auth/",
    endpoint=auth,
    methods=["POST"],
    summary="Auth Token 签发/刷新",
    tags=["auth"],
)

router.add_api_route(
    path="/refreshToken/",
    endpoint=refresh_token,
    methods=["POST"],
    summary="刷新访问Token",
    tags=["auth"],
)

router.add_api_route(
    path="/phoneCode/",
    endpoint=phone_code,
    methods=["POST"],
    summary="发送手机验证码",
    tags=["auth"],
)

router.add_api_route(
    path="/phoneCodeLogin/",
    endpoint=phone_code_login,
    methods=["POST"],
    summary="手机验证码登录",
    tags=["auth"],
)

router.add_api_route(
    path="/v2Active/",
    endpoint=v2_active,
    methods=["POST"],
    summary="V2设备激活",
    tags=["device"],
)

router.add_api_route(
    path="/updateClientidAndMac/",
    endpoint=update_clientid_mac,
    methods=["POST"],
    summary="更新客户端ID和MAC",
    tags=["device"],
)

router.add_api_route(
    path="/btBuds/",
    endpoint=bt_buds,
    methods=["POST"],
    summary="蓝牙耳机设备查询",
    tags=["device"],
)

router.add_api_route(
    path="/translate/",
    endpoint=translate,
    methods=["POST"],
    summary="文本翻译",
    tags=["ai"],
)

router.add_api_route(
    path="/summary/",
    endpoint=summary,
    methods=["POST"],
    summary="内容总结",
    tags=["ai"],
)

router.add_api_route(
    path="/text2Img/",
    endpoint=text2img,
    methods=["POST"],
    summary="文字生成图片",
    tags=["ai"],
)

router.add_api_route(
    path="/gpt3Assistant/",
    endpoint=gpt3_assistant,
    methods=["POST"],
    summary="GPT3 助手对话",
    tags=["ai"],
)

router.add_api_route(
    path="/phoneLogin/",
    endpoint=phone_login,
    methods=["POST"],
    summary="手机号登录",
    tags=["auth"],
)

router.add_api_route(
    path="/emailLogin/",
    endpoint=email_login,
    methods=["POST"],
    summary="邮箱登录",
    tags=["auth"],
)

router.add_api_route(
    path="/appleLogin/",
    endpoint=apple_login,
    methods=["POST"],
    summary="Apple登录",
    tags=["auth"],
)

router.add_api_route(
    path="/subLogin/",
    endpoint=sub_login,
    methods=["POST"],
    summary="Google/X订阅登录",
    tags=["auth"],
)

router.add_api_route(
    path="/active/",
    endpoint=active,
    methods=["POST"],
    summary="V1设备激活",
    tags=["device"],
)

router.add_api_route(
    path="/img2Img/",
    endpoint=img2img,
    methods=["POST"],
    summary="图片生成图片",
    tags=["ai"],
)

# P2/P3 阶段新增路由 - 记录相关
router.add_api_route(
    path="/audioRecord/",
    endpoint=audio_record,
    methods=["POST"],
    summary="查询音频记录",
    tags=["record"],
)

router.add_api_route(
    path="/assistantRecord/",
    endpoint=assistant_record,
    methods=["POST"],
    summary="查询助手记录",
    tags=["record"],
)

router.add_api_route(
    path="/musicRecord/",
    endpoint=music_record,
    methods=["POST"],
    summary="音乐使用记录",
    tags=["record"],
)

router.add_api_route(
    path="/recordDuration/",
    endpoint=record_duration,
    methods=["POST"],
    summary="录音时长记录",
    tags=["record"],
)

router.add_api_route(
    path="/deleteRecord/",
    endpoint=delete_record,
    methods=["POST"],
    summary="删除音频记录",
    tags=["record"],
)

# P2/P3 阶段新增路由 - 配置相关
router.add_api_route(
    path="/prompt/",
    endpoint=prompt,
    methods=["POST"],
    summary="获取提示词",
    tags=["config"],
)

router.add_api_route(
    path="/music/",
    endpoint=music,
    methods=["POST"],
    summary="获取音乐列表",
    tags=["config"],
)

router.add_api_route(
    path="/musicCDN/",
    endpoint=music_cdn,
    methods=["POST"],
    summary="获取音乐CDN配置",
    tags=["config"],
)

router.add_api_route(
    path="/musicCategoriesList/",
    endpoint=music_categories_list,
    methods=["POST"],
    summary="获取音乐分类列表",
    tags=["config"],
)

router.add_api_route(
    path="/weatherInfo/",
    endpoint=weather_info,
    methods=["POST"],
    summary="获取天气信息",
    tags=["config"],
)

# P2/P3 阶段新增路由 - 壁纸相关
router.add_api_route(
    path="/wallpaperList/",
    endpoint=wallpaper_list,
    methods=["POST"],
    summary="获取壁纸列表",
    tags=["wallpaper"],
)

router.add_api_route(
    path="/wallpaperDelete/",
    endpoint=wallpaper_delete,
    methods=["POST"],
    summary="删除壁纸",
    tags=["wallpaper"],
)

# P2/P3 阶段新增路由 - 上传相关
router.add_api_route(
    path="/uploadAudio/",
    endpoint=upload_audio,
    methods=["POST"],
    summary="上传音频文件",
    tags=["upload"],
)

router.add_api_route(
    path="/uploadWallpaper/",
    endpoint=upload_wallpaper,
    methods=["POST"],
    summary="上传壁纸文件",
    tags=["upload"],
)

# P2/P3 阶段新增路由 - 音乐收藏相关
router.add_api_route(
    path="/musicFavorite/",
    endpoint=music_favorite,
    methods=["POST"],
    summary="音乐收藏/取消",
    tags=["music"],
)

router.add_api_route(
    path="/musicFavoriteList/",
    endpoint=music_favorite_list,
    methods=["POST"],
    summary="获取音乐收藏列表",
    tags=["music"],
)

router.add_api_route(
    path="/musicPlayReport/",
    endpoint=music_play_report,
    methods=["POST"],
    summary="音乐播放上报",
    tags=["music"],
)

# P2/P3 阶段新增路由 - OTA相关
router.add_api_route(
    path="/otaCheck/",
    endpoint=ota_check,
    methods=["POST"],
    summary="OTA固件检查",
    tags=["ota"],
)
