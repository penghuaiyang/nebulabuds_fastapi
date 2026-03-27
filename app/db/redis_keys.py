import json
import os
from pathlib import Path

# 加载 client_db_start 映射（来自旧项目）
_CLIENT_DB_START_PATH = Path(__file__).parent / "db_start.json"


def _load_client_db_start() -> dict:
    """懒加载 client_db_start 映射"""
    if not hasattr(_load_client_db_start, "_cache"):
        if _CLIENT_DB_START_PATH.exists():
            with open(_CLIENT_DB_START_PATH, "r", encoding="utf-8") as f:
                _load_client_db_start._cache = json.load(f)
        else:
            _load_client_db_start._cache = {}
    return _load_client_db_start._cache


def _get_db_offset(clientid: str) -> int:
    """根据 clientid 获取 db 偏移量"""
    db_start = _load_client_db_start()
    return db_start.get(clientid, 0)


class RedisKeys:
    # ===================== 固定 key（不涉及 db 编号） =====================
    USER_ID_SEQ = "user_id_seq"
    DEVICE_USER_ID = "device_user_id"
    DEVICE_INFO = "device:info"
    MAX_USERID = "max_userid"

    # ===================== 设备与用户映射 =====================
    @staticmethod
    def device_user_id(device_id: str) -> str:
        """deviceid -> userid 映射"""
        return f"device_userid:{device_id}"

    @staticmethod
    def user_profile(userid: int) -> str:
        """userid -> user profile 缓存"""
        return f"30:user:profile:{userid}"

    @staticmethod
    def join_device_lock(device_id: str) -> str:
        """Join 接口的 deviceid 分布式锁"""
        return f"join_lock:{device_id}"

    @staticmethod
    def email_code(email: str) -> str:
        """邮箱验证码"""
        return f"email:code:{email}"

    @staticmethod
    def sms_code(phone_no: str) -> str:
        """短信验证码"""
        return f"sms:code:{phone_no}"

    @staticmethod
    def record_duration(userid: int) -> str:
        """录音时长（原 db=7）"""
        return f"7:record:user:{userid}:duration"

    @staticmethod
    def ai_num(userid: int, clientid: str = "") -> str:
        """AI 使用次数（db=8 + clientid偏移）

        旧系统：db = AI_NUM_DB(8) + CLIENT_DB_START[clientid]
        """
        offset = _get_db_offset(clientid)
        return f"{8 + offset}:ai:user:{userid}:num"

    @staticmethod
    def music_num(userid: int) -> str:
        """音乐使用次数（原 db=10）"""
        return f"10:music:user:{userid}:num"

    @staticmethod
    def btname_list(userid: int) -> str:
        """蓝牙名称列表（原 db=14，List 结构）"""
        return f"14:btname:user:{userid}:list"

    @staticmethod
    def mac_active_code(userid: int) -> str:
        """mac -> activeCode Hash（原 db=23）"""
        return f"23:mac:user:{userid}:active_code"

    @staticmethod
    def mac_clientid(userid: int) -> str:
        """mac -> clientid Hash（原 db=24）"""
        return f"24:mac:user:{userid}:clientid"

    @staticmethod
    def free_record_date(userid: int) -> str:
        """免费录音到期时间（原 db=25）"""
        return f"25:record:user:{userid}:free_date"

    @staticmethod
    def record_rest(userid: int) -> str:
        """录音剩余时间（原 db=29）"""
        return f"29:record:user:{userid}:rest"

    @staticmethod
    def single_max_duration(clientid: str = "") -> str:
        """单次最大使用时长配置（原 db=0）
        - 无 clientid 时为全局配置
        - 有 clientid 时为 clientid 级配置
        """
        if clientid:
            return f"0:config:app:single_max_duration:{clientid}"
        return "0:config:app:single_max_duration"

    # ===================== GPT AI 对话相关 =====================

    @staticmethod
    def ai_day_num(userid: int) -> str:
        """AI 日使用次数（原 db=26）

        用于记录用户每日使用 AI 对话的次数，实现每日次数限制。
        """
        return f"26:ai:day:num:{userid}"

    @staticmethod
    def gpt_conversation(userid: int) -> str:
        """GPT 会话 ID（原 db=17）

        用于保持 GPT 对话的上下文连续性。
        """
        return f"17:gpt:conversation:{userid}"
