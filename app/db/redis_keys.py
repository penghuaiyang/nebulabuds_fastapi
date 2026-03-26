class RedisKeys:
    # ===================== 固定 key =====================
    USER_ID_SEQ = "user_id_seq"
    DEVICE_USER_ID = "device_user_id"

    # ===================== 设备与用户映射 =====================
    @staticmethod
    def device_user_id(device_id: str):
        """deviceid -> userid 映射"""
        return f"device_userid:{device_id}"

    @staticmethod
    def email_code(email: str):
        """邮箱验证码"""
        return f"email:code:{email}"

    @staticmethod
    def sms_code(phone_no: str):
        """短信验证码"""
        return f"sms:code:{phone_no}"

    @staticmethod
    def macaddr_benefit_duration(macaddr: str):
        """MAC 当前权益 duration_config"""
        return f"macaddr_benefit_duration:{macaddr}"

    # ===================== 其他业务 =====================
    DEVICE_INFO = "device:info"
    MAX_USERID = "max_userid"
