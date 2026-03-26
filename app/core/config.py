import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class IdentityType:
    DEVICE = "device"
    EMAIL = "email"
    PHONE = "phone"
    GOOGLE = "google"
    APPLE = "apple"
    X = "x"


class NicknameDefaults:
    GUEST_USER = "guest user"
    NEW_USER = "new user"


class Settings:
    # App
    app_name: str = os.getenv("APP_NAME", "recycle-dashboard-api")
    env: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8000"))
    log_dir: str = os.getenv("LOG_DIR", "logs")

    # MySQL (async driver: asyncmy)
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "Hhs999ah.")
    mysql_host: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_db: str = os.getenv("MYSQL_DB", "recycle")

    # Redis (cache + Celery broker/backend + WS pub/sub)
    redis_host: str = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    # JWT / Auth
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_expires_minutes: int = int(os.getenv("ACCESS_EXPIRES_MINUTES", "10080"))  # default 7 days
    refresh_expires_days: int = int(os.getenv("REFRESH_EXPIRES_DAYS", "30"))  # default 7 days

    # JWT / Auth (Admin)
    jwt_admin_secret_key: str = os.getenv("JWT_ADMIN_SECRET_KEY", "admin-secret-key-change-me")
    jwt_admin_algorithm: str = os.getenv("JWT_ADMIN_ALGORITHM", "HS256")
    jwt_admin_access_expires_minutes: int = int(os.getenv("JWT_ADMIN_ACCESS_EXPIRES_MINUTES", "480"))  # default 8 hours
    jwt_admin_refresh_expires_days: int = int(os.getenv("JWT_ADMIN_REFRESH_EXPIRES_DAYS", "7"))  # default 7 days

    # Admin Auth
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")

    fixed_otp_code: str = os.getenv("FIXED_OTP_CODE", "1234")  # dev backdoor SMS code
    sms_fixed_code: str = os.getenv("SMS_FIXED_CODE", "1234")

    # Email (SMTP)
    email_sender: str = os.getenv("EMAIL_SENDER", "")
    email_sender_alias: str = os.getenv("EMAIL_SENDER_ALIAS", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "465"))
    email_code_expiry_minutes: int = int(os.getenv("EMAIL_CODE_EXPIRY_MINUTES", "5"))
    email_fixed_code: str = os.getenv("EMAIL_FIXED_CODE", "0723")
    sms_code_expiry_minutes: int = int(os.getenv("SMS_CODE_EXPIRY_MINUTES", "5"))

    # Aliyun SMS
    aliyun_sms_access_key_id: str = os.getenv("ALIYUN_SMS_ACCESS_KEY_ID", "")
    aliyun_sms_access_key_secret: str = os.getenv("ALIYUN_SMS_ACCESS_KEY_SECRET", "")
    aliyun_sms_sign_name: str = os.getenv("ALIYUN_SMS_SIGN_NAME", "")
    aliyun_sms_template_code: str = os.getenv("ALIYUN_SMS_TEMPLATE_CODE", "")
    aliyun_sms_endpoint: str = os.getenv("ALIYUN_SMS_ENDPOINT", "dysmsapi.aliyuncs.com")

    # Apple Login
    apple_client_id: str = os.getenv("APPLE_CLIENT_ID", "")
    apple_issuer: str = os.getenv("APPLE_ISSUER", "https://appleid.apple.com")
    apple_jwks_url: str = os.getenv("APPLE_JWKS_URL", "https://appleid.apple.com/auth/keys")

    # Google Login
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_issuer: str = os.getenv("GOOGLE_ISSUER", "https://accounts.google.com")
    google_jwks_url: str = os.getenv("GOOGLE_JWKS_URL", "https://www.googleapis.com/oauth2/v3/certs")

    # WeChat Pay (Native)
    wechat_appid: str = os.getenv("WECHAT_APPID", "")
    wechat_mchid: str = os.getenv("WECHAT_MCHID", "")
    wechat_serial_no: str = os.getenv("WECHAT_SERIAL_NO", "")
    wechat_notify_url: str = os.getenv("WECHAT_NOTIFY_URL", "")
    wechat_api_v3_key: str = os.getenv("WECHAT_API_V3_KEY", "")
    wechat_private_key_path: str = os.getenv("WECHAT_PRIVATE_KEY_PATH", "")
    wechat_cert_dir: str = os.getenv("WECHAT_CERT_DIR", "")

    # llm
    qwen_base_url = os.getenv("QWEN_BASE_URL", "")
    qwen_api_key = os.getenv("QWEN_API_KEY", "")
    qwen_model_id = os.getenv("QWEN_MODEL_ID", "")
    translate_base_url: str = os.getenv("TRANSLATE_BASE_URL", "https://jmjapaneast.openai.azure.com/openai/deployments/gpt-4.1-mini/chat/completions?api-version=2024-12-01-preview")
    # translate_base_url: str = os.getenv("TRANSLATE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    translate_api_key: str = os.getenv("TRANSLATE_API_KEY", "")
    # translate_api_key: str = os.getenv("TRANSLATE_API_KEY", "sk-6a7c450b22084034939d96ec57e342b6")
    translate_model_id: str = os.getenv("TRANSLATE_MODEL_ID", "")
    # translate_model_id: str = os.getenv("TRANSLATE_MODEL_ID", "qwen-mt-flash")
    translate_timeout_seconds: float = float(os.getenv("TRANSLATE_TIMEOUT_SECONDS", "120"))
    translate_temperature: float = float(os.getenv("TRANSLATE_TEMPERATURE", "0.2"))

    # 阿里云百炼 Qwen-MT 机器翻译
    mt_translate_base_url: str = os.getenv("MT_TRANSLATE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    mt_translate_api_key: str = os.getenv("MT_TRANSLATE_API_KEY", "")
    mt_translate_model_id: str = os.getenv("MT_TRANSLATE_MODEL_ID", "")
    mt_translate_timeout_seconds: float = float(os.getenv("MT_TRANSLATE_TIMEOUT_SECONDS", "120"))

    # taskiq
    broker_url: str = os.getenv("BROKER_URL", "redis://127.0.0.1:6379/1")
    result_backend_url: str = os.getenv("RESULT_BACKEND_URL", "redis://127.0.0.1:6379/1")

    # Tencent COS
    tencent_secret_id: str = os.getenv("TENCENT_SECRET_ID", "")
    tencent_secret_key: str = os.getenv("TENCENT_SECRET_KEY", "")


    # Tencent ASR (WebSocket)
    tencent_asr_appid: str = os.getenv("TENCENT_ASR_APPID", "")
    tencent_asr_secret_id: str = os.getenv("TENCENT_ASR_SECRET_ID", "")
    tencent_asr_secret_key: str = os.getenv("TENCENT_ASR_SECRET_KEY", "")
    tencent_asr_engine_model_type: str = os.getenv("TENCENT_ASR_ENGINE_MODEL_TYPE", "16k_zh")
    tencent_asr_voice_format: int = int(os.getenv("TENCENT_ASR_VOICE_FORMAT", "1"))
    tencent_asr_needvad: int = int(os.getenv("TENCENT_ASR_NEEDVAD", "1"))
    tencent_asr_filter_dirty: int = int(os.getenv("TENCENT_ASR_FILTER_DIRTY", "0"))
    tencent_asr_filter_modal: int = int(os.getenv("TENCENT_ASR_FILTER_MODAL", "0"))
    tencent_asr_filter_punc: int = int(os.getenv("TENCENT_ASR_FILTER_PUNC", "0"))
    tencent_asr_convert_num_mode: int = int(os.getenv("TENCENT_ASR_CONVERT_NUM_MODE", "1"))
    tencent_asr_word_info: int = int(os.getenv("TENCENT_ASR_WORD_INFO", "0"))
    tencent_asr_vad_silence_time: int = int(os.getenv("TENCENT_ASR_VAD_SILENCE_TIME", "800"))
    tencent_asr_max_speak_time: int = int(os.getenv("TENCENT_ASR_MAX_SPEAK_TIME", "20000"))
    tencent_asr_noise_threshold: float = float(os.getenv("TENCENT_ASR_NOISE_THRESHOLD", "1.5"))
    tencent_asr_expired_seconds: int = int(os.getenv("TENCENT_ASR_EXPIRED_SECONDS", "600"))

    # Azure Speech ASR
    azure_speech_key: str = os.getenv("AZURE_SPEECH_KEY", "")
    azure_speech_region: str = os.getenv("AZURE_SPEECH_REGION", "japaneast")
    azure_asr_language: str = os.getenv("AZURE_ASR_LANGUAGE", "zh-CN")
    azure_asr_sample_rate: int = int(os.getenv("AZURE_ASR_SAMPLE_RATE", "16000"))
    azure_asr_channels: int = int(os.getenv("AZURE_ASR_CHANNELS", "1"))
    azure_asr_audio_format: str = os.getenv("AZURE_ASR_AUDIO_FORMAT", "pcm")
    azure_tts_api_key: str = os.getenv("AZURE_TTS_API_KEY", "")
    azure_tts_region: str = os.getenv("AZURE_TTS_REGION", "japaneast")
    azure_tts_voice: str = os.getenv("AZURE_TTS_VOICE", "zh-CN-XiaoxiaoNeural")
    azure_tts_output_format: str = os.getenv("AZURE_TTS_OUTPUT_FORMAT", "Raw16Khz16BitMonoPcm")
    azure_tts_endpoint: str = os.getenv("AZURE_TTS_ENDPOINT", "")
    azure_tts_frame_timeout_interval: str = os.getenv("AZURE_TTS_FRAME_TIMEOUT_INTERVAL", "100000000")
    azure_tts_rtf_timeout_threshold: str = os.getenv("AZURE_TTS_RTF_TIMEOUT_THRESHOLD", "10")
    tts_cos_bucket_id: str = os.getenv("TTS_COS_BUCKET_ID", "voxigo-1325519451")
    tts_cos_region: str = os.getenv("TTS_COS_REGION", "ap-shanghai")
    tts_download_url_expires: int = int(os.getenv("TTS_DOWNLOAD_URL_EXPIRES", "43200"))
    tts_text_max_length: int = int(os.getenv("TTS_TEXT_MAX_LENGTH", "500"))
    word_image_cos_bucket_id: str = os.getenv("WORD_IMAGE_COS_BUCKET_ID", os.getenv("TTS_COS_BUCKET_ID", "voxigo-1325519451"))
    word_image_cos_region: str = os.getenv("WORD_IMAGE_COS_REGION", os.getenv("TTS_COS_REGION", "ap-shanghai"))
    word_image_cos_prefix: str = os.getenv("WORD_IMAGE_COS_PREFIX", "word_images")
    word_image_base_url: str = os.getenv("WORD_IMAGE_BASE_URL", "")
    word_image_download_url_expires: int = int(os.getenv("WORD_IMAGE_DOWNLOAD_URL_EXPIRES", "43200"))
    word_image_manifest_path: str = os.getenv(
        "WORD_IMAGE_MANIFEST_PATH",
        os.path.join(os.path.dirname(__file__), "word_images_manifest.json"),
    )

    device_type: dict = {
        1: "耳机",
        2: "手表",
    }

    # ===================== 产品类型配置 =====================
    # 产品类型枚举：1-样机，2-大货
    product_type: dict = {
        1: "样机",
        2: "大货",
    }

    # ===================== MAC 类型配置 =====================
    # MAC 类型枚举：1-BLE，2-经典蓝牙
    mac_type: dict = {
        1: "BLE",
        2: "经典蓝牙",
    }

    # ===================== 权益扣费场景配置 =====================
    benefit_deduction_scene: dict = {
        1: "场景跟读",
        2: "实时翻译",
    }

    #  设备激活类型枚举
    active_type: dict = {
        1: "BLE",
        2: "经典蓝牙",
        3: "激活码",
    }


    # ===================== 激活码配置 =====================
    # 激活码默认长度
    active_code_length: int = int(os.getenv("ACTIVE_CODE_LENGTH", "8"))
    # 激活码序号起始值
    active_code_serial_start: int = int(os.getenv("ACTIVE_CODE_SERIAL_START", "10000000"))

    # ===================== MAC 地址配置 =====================
    # MAC 地址序号起始值
    mac_address_serial_start: int = int(os.getenv("MAC_ADDRESS_SERIAL_START", "10000000"))

    @property
    def mysql_dsn(self) -> str:
        # asyncmy driver DSN
        return (
            f"mysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}?charset=utf8mb4"
        )

    @property
    def redis_dsn(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache()
def get_settings() -> Settings:
    # Cached settings instance to avoid re-reading envs.
    return Settings()


settings = get_settings()
