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
    def macaddr_benefit_duration(macaddr: str) -> str:
        """MAC 当前权益 duration_config"""
        return f"macaddr_benefit_duration:{macaddr}"

    # ===================== Login 业务 Redis（统一 db={N}:{namespace}:... 格式） =====================
    # 格式: {db}:{namespace}:{scope}:{identifier}:{field?}

    @staticmethod
    def record_duration(userid: str) -> str:
        """录音时长（原 db=7）"""
        return f"7:record:user:{userid}:duration"

    @staticmethod
    def ai_num(userid: str) -> str:
        """AI 使用次数（原 db=8）"""
        return f"8:ai:user:{userid}:num"

    @staticmethod
    def music_num(userid: str) -> str:
        """音乐使用次数（原 db=10）"""
        return f"10:music:user:{userid}:num"

    @staticmethod
    def btname_list(userid: str) -> str:
        """蓝牙名称列表（原 db=14，List 结构）"""
        return f"14:btname:user:{userid}:list"

    @staticmethod
    def mac_active_code(userid: str) -> str:
        """mac -> activeCode Hash（原 db=23）"""
        return f"23:mac:user:{userid}:active_code"

    @staticmethod
    def mac_clientid(userid: str) -> str:
        """mac -> clientid Hash（原 db=24）"""
        return f"24:mac:user:{userid}:clientid"

    @staticmethod
    def free_record_date(userid: str) -> str:
        """免费录音到期时间（原 db=25）"""
        return f"25:record:user:{userid}:free_date"

    @staticmethod
    def record_rest(userid: str) -> str:
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
