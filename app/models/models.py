from tortoise import fields
from tortoise.models import Model


class TranslationCache(Model):
    id = fields.IntField(pk=True)
    source_text = fields.TextField()
    source_hash = fields.CharField(max_length=64, index=True)
    target_language = fields.CharField(max_length=16)
    translated_text = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "translation_cache"
        unique_together = ("source_hash", "target_language")



class User(Model):
    id = fields.IntField(pk=True)
    userid = fields.IntField()
    deviceid = fields.CharField(max_length=64)
    clientCode = fields.CharField(max_length=64)
    macInfo = fields.CharField(max_length=1024, null=True)
    phoneNo = fields.CharField(max_length=32, null=True)
    wechatid = fields.CharField(max_length=32, null=True)
    unionid = fields.CharField(max_length=32, null=True)
    appleid = fields.CharField(max_length=32, null=True)
    platForm = fields.IntField(description="0=ios,1=android")
    nation = fields.CharField(max_length=32)
    localLanguage = fields.CharField(max_length=32)
    brand = fields.CharField(max_length=32)
    nickName = fields.CharField(max_length=32)
    avartar = fields.CharField(max_length=64)
    vip = fields.IntField(default=0)
    email = fields.CharField(max_length=32, default="0")
    password = fields.CharField(max_length=32, null=True)
    loginName = fields.CharField(max_length=32, null=True)
    mac = fields.CharField(max_length=64, null=True)
    time = fields.BigIntField()

    class Meta:
        table = "user"

    async def to_dict(self):
        return {
            "id": self.id,
            "userid": self.userid,
            "deviceid": self.deviceid,
            "clientCode": self.clientCode,
            "macInfo": self.macInfo,
            "phoneNo": self.phoneNo,
            "appleid": self.appleid,
            "platForm": self.platForm,
            "nation": self.nation,
            "localLanguage": self.localLanguage,
            "brand": self.brand,
            "nickName": self.nickName,
            "email": self.email,
            "time": self.time,
        }


class PurchasedRecord(Model):
    id = fields.IntField(pk=True)
    userid = fields.IntField()
    price = fields.FloatField(default=0)
    payType = fields.IntField(
        description="0=appstore 内购 1= 微信支付 2= 支付宝支付 3=Fwatch支付"
    )
    time = fields.BigIntField()
    tradeNo = fields.CharField(max_length=64)
    payFrom = fields.CharField(max_length=64, null=True)
    refund = fields.IntField(default=0)
    status = fields.IntField(default=0)
    payFor = fields.CharField(max_length=64, default="vip")

    class Meta:
        table = "purchasedRecord"

    async def to_dict(self):
        return {
            "id": self.id,
            "userid": self.userid,
            "price": self.price,
            "payType": self.payType,
            "time": self.time,
            "tradeNo": self.tradeNo,
            "payFrom": self.payFrom,
            "refund": self.refund,
            "status": self.status,
            "payFor": self.payFor,
        }


class ActiveFalse(Model):
    id = fields.IntField(pk=True)
    userid = fields.CharField(max_length=255, null=True)
    activeCode = fields.CharField(max_length=128)
    btName = fields.CharField(max_length=255, null=True)
    macAddr = fields.CharField(max_length=255, null=True)
    active = fields.IntField(default=0)
    description = fields.CharField(max_length=255)
    importTime = fields.BigIntField()

    class Meta:
        table = "activeFalse"
        table_description = "Active False Record Table"
        indexes = [
            ("activeCode",),
            ("userid",),
        ]

    async def to_dict(self):
        return {
            "id": self.id,
            "userid": self.userid,
            "activeCode": self.activeCode,
            "btName": self.btName,
            "macAddr": self.macAddr,
            "active": self.active,
            "description": self.description,
            "importTime": self.importTime,
        }


class Buds(Model):
    id = fields.IntField(pk=True)
    brandId = fields.IntField()
    name = fields.CharField(max_length=128)
    image = fields.CharField(max_length=128)
    introduction = fields.TextField()
    blName = fields.CharField(max_length=64)
    ifScreen = fields.IntField(default=0, description="0 不带屏 1 带屏 2 杰理")
    connectType = fields.IntField(
        default=1, description="1 ble 2 btMac 3 huawei 4 activeCode"
    )
    deviceType = fields.IntField(default=1)
    wallName = fields.CharField(max_length=64, null=True)
    time = fields.BigIntField()

    class Meta:
        table = "buds"

    async def to_dict(self):
        return {
            "id": self.id,
            "brandId": self.brandId,
            "name": self.name,
            "image": self.image,
            "introduction": self.introduction,
            "blName": self.blName,
            "ifScreen": self.ifScreen,
            "connectType": self.connectType,
            "deviceType": self.deviceType,
            "wallName": self.wallName,
            "time": self.time,
        }


class BudsBrand(Model):
    id = fields.IntField(pk=True)
    clientId = fields.CharField(max_length=32)
    brandName = fields.CharField(max_length=128)
    image = fields.CharField(max_length=256)
    time = fields.BigIntField()

    class Meta:
        table = "budsBrand"

    async def to_dict(self):
        return {
            "id": self.id,
            "clientId": self.clientId,
            "brandName": self.brandName,
            "image": self.image,
            "time": self.time,
        }


class BulkActiveCode(Model):
    id = fields.IntField(pk=True)
    clientCode = fields.CharField(max_length=32, null=True)
    btName = fields.CharField(max_length=64, null=True)  #
    code = fields.CharField(max_length=128, unique=True)
    active = fields.IntField(default=0)
    importTime = fields.BigIntField()
    activeTime = fields.BigIntField(default=0)
    codeType = fields.IntField(null=True)  #
    deviceType = fields.IntField(null=True)  #
    userid = fields.IntField(null=True)
    macAddr = fields.CharField(max_length=128, null=True)

    class Meta:
        table = "BulkActiveCode"
        indexes = [
            ("clientCode",),
        ]

    async def to_dict(self):
        return {
            "id": self.id,
            "clientCode": self.clientCode,
            "btName": self.btName,
            "code": self.code,
            "active": self.active,
            "importTime": self.importTime,
            "activeTime": self.activeTime,
            "codeType": self.codeType,
            "deviceType": self.deviceType,
            "userid": self.userid,
            "macAddr": self.macAddr,
        }


class Translation(Model):
    id = fields.IntField(pk=True)
    source_text = fields.TextField()
    translated_text = fields.TextField(null=True)
    source_language = fields.CharField(max_length=16)
    target_language = fields.CharField(max_length=16)
    source_key = fields.CharField(
        max_length=128,
        unique=True,
        description="md5(source_text+source_lang+target_lang)",
    )
    status = fields.IntField(default=0, description="0=pending,1=done,2=failed")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_used_at = fields.DatetimeField(null=True)

    class Meta:
        table = "translations"
        indexes = [
            ("source_language", "target_language"),
            ("status",),
        ]

    async def to_dict(self):
        return {
            "id": self.id,
            "source_text": self.source_text,
            "translated_text": self.translated_text,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "source_key": self.source_key,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_used_at": self.last_used_at,
        }


class GiftActiveCode(Model):
    id = fields.IntField(pk=True)
    clientCode = fields.CharField(max_length=32, null=True)
    btName = fields.CharField(max_length=64, null=True)
    code = fields.CharField(max_length=128, unique=True)
    active = fields.IntField(default=0)
    importTime = fields.BigIntField()
    activeTime = fields.BigIntField(default=0)
    codeType = fields.IntField(null=True)
    deviceType = fields.IntField(null=True)
    userid = fields.IntField(null=True)
    macAddr = fields.CharField(max_length=128, null=True)

    class Meta:
        table = "giftActiveCode"
        indexes = [
            ("clientCode",),
        ]

    async def to_dict(self):
        return {
            "id": self.id,
            "clientCode": self.clientCode,
            "btName": self.btName,
            "code": self.code,
            "active": self.active,
            "importTime": self.importTime,
            "activeTime": self.activeTime,
            "codeType": self.codeType,
            "deviceType": self.deviceType,
            "userid": self.userid,
            "macAddr": self.macAddr,
        }


class ActiveCode(Model):
    id = fields.IntField(pk=True)
    userid = fields.IntField(null=True)
    macAddr = fields.CharField(max_length=128, null=True)
    clientCode = fields.CharField(max_length=32)
    btName = fields.CharField(max_length=64, null=True)
    code = fields.CharField(max_length=128, unique=True)
    active = fields.IntField(default=0)
    importTime = fields.BigIntField()
    activeTime = fields.BigIntField(default=0)
    codeType = fields.IntField(default=1)
    deviceType = fields.IntField(default=1)

    class Meta:
        table = "activeCode"
        indexes = [
            ("clientCode",),
        ]

    async def to_dict(self):
        return {
            "id": self.id,
            "userid": self.userid,
            "macAddr": self.macAddr,
            "clientCode": self.clientCode,
            "btName": self.btName,
            "code": self.code,
            "active": self.active,
            "importTime": self.importTime,
            "activeTime": self.activeTime,
            "codeType": self.codeType,
            "deviceType": self.deviceType,
        }


class ActiveRecord(Model):
    id = fields.IntField(pk=True)
    clientid = fields.CharField(max_length=64)
    mac = fields.CharField(max_length=64)
    userid = fields.IntField()
    time = fields.BigIntField()
    activeType = fields.IntField(default=1)
    bt_name = fields.CharField(max_length=64, null=True)

    class Meta:
        table = "activeRecord"
        indexes = [
            ("clientid",),
            ("mac",),
            ("userid",),
        ]

    async def to_dict(self):
        return {
            "id": self.id,
            "clientid": self.clientid,
            "mac": self.mac,
            "userid": self.userid,
            "time": self.time,
            "activeType": self.activeType,
            "bt_name": self.bt_name,
        }


class Mac(Model):
    id = fields.IntField(pk=True)
    clientCode = fields.CharField(max_length=32)
    btName = fields.CharField(max_length=64, null=True)
    macAddr = fields.CharField(max_length=128)
    active = fields.IntField(default=0)
    importTime = fields.BigIntField()
    activeTime = fields.BigIntField(default=0)
    macType = fields.IntField(default=1)
    deviceType = fields.IntField(default=1)
    activeType = fields.IntField(default=1)

    class Meta:
        table = "mac"
        indexes = [("clientCode",)]

    async def to_dict(self):
        return {
            "id": self.id,
            "clientCode": self.clientCode,
            "btName": self.btName,
            "macAddr": self.macAddr,
            "active": self.active,
            "importTime": self.importTime,
            "activeTime": self.activeTime,
            "macType": self.macType,
            "deviceType": self.deviceType,
            "activeType": self.activeType,
        }


class MacFalse(Model):
    id = fields.IntField(pk=True)
    clientCode = fields.CharField(max_length=32)
    macAddr = fields.CharField(max_length=128)
    active = fields.IntField(default=0)
    activeType = fields.IntField(default=1)
    importTime = fields.BigIntField()

    class Meta:
        table = "macFalse"


class Customer(Model):
    id = fields.IntField(pk=True)
    password = fields.CharField(max_length=64)
    companyName = fields.CharField(max_length=64)
    phoneNo = fields.CharField(max_length=64, unique=True)
    email = fields.CharField(max_length=64)
    clientid = fields.CharField(max_length=64)
    time = fields.BigIntField()

    class Meta:
        table = "customer"
        ordering = ["id"]

    async def to_dict(self):
        return {
            "id": self.id,
            "password": self.password,
            "companyName": self.companyName,
            "phoneNo": self.phoneNo,
            "email": self.email,
            "clientid": self.clientid,
            "time": self.time,
        }


class DeviceHiddenFunction(Model):
    id = fields.IntField(pk=True)
    device_name = fields.CharField(max_length=64, description="设备名")
    hidden_function = fields.CharField(max_length=64, description="功能id")
    time = fields.BigIntField(description="时间戳")

    class Meta:
        table = "device_hidden_function"

    async def to_dict(self):
        return {
            "id": self.id,
            "device_name": self.device_name,
            "hidden_function": self.hidden_function,
            "time": self.time,
        }


class MacType(Model):
    id = fields.IntField(pk=True)
    mac_type = fields.CharField(max_length=64)
    description = fields.CharField(max_length=64)
    time = fields.BigIntField()

    class Meta:
        table = "mac_type"  # 指定表名
        ordering = ["id"]  # 指定默认排序字段

    async def to_dict(self):
        return {
            "id": self.id,
            "mac_type": self.mac_type,
            "description": self.description,
            "time": self.time,
        }


class DeviceType(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64)
    device_type = fields.CharField(max_length=64)
    time = fields.BigIntField(description="时间戳")

    class Meta:
        table = "device_type"  # 指定表名

    async def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "device_type": self.device_type,
            "time": self.time,
        }


class Task(Model):
    id = fields.IntField(pk=True)
    task_type = fields.CharField(
        max_length=15, description="1.重置大货激活码 2.重置样机激活码 3.重置礼品激活码"
    )
    task_id = fields.CharField(max_length=25, unique=True)
    description = fields.CharField(max_length=64)
    time = fields.BigIntField()

    class Meta:
        table = "task"
        table_description = "任务表，记录激活码重置任务"
        indexes = ("task_id",)

    async def to_dict(self):
        return {
            "id": self.id,
            "task_type": self.task_type,
            "task_id": self.task_id,
            "description": self.description,
            "time": self.time,
        }


class AudioRecord(Model):
    id = fields.IntField(pk=True)
    clientCode = fields.CharField(max_length=64)
    userid = fields.IntField()
    poi = fields.CharField(max_length=128, null=True)
    path = fields.CharField(max_length=64)
    content = fields.TextField()
    summary = fields.TextField(null=True)
    contentWithRoles = fields.TextField(null=True)
    translate = fields.TextField()
    duration = fields.IntField()
    phoneNo = fields.CharField(max_length=32, null=True)
    audioType = fields.IntField(
        description="0=电话录音，1=手机视频，音频，录音，2=现场录音，会议录音，3=同听传译，4=面对面翻译"
    )
    time = fields.BigIntField()

    class Meta:
        table = "audioRecord"
        table_description = "音频记录表"
        indexes = ["clientCode", "userid"]

    async def to_dict(self):
        return {
            "id": self.id,
            "clientCode": self.clientCode,
            "userid": self.userid,
            "poi": self.poi,
            "path": self.path,
            "content": self.content,
            "summary": self.summary,
            "contentWithRoles": self.contentWithRoles,
            "translate": self.translate,
            "duration": self.duration,
            "phoneNo": self.phoneNo,
            "audioType": self.audioType,
            "time": self.time,
        }


class FuncSummary(Model):
    id = fields.IntField(pk=True)  # 主键，自增
    userid = fields.CharField(max_length=15)
    clientid = fields.CharField(max_length=25, null=True, description="客户id")
    funcType = fields.IntField(
        description="1.同声传译 2.耳机+手机 3.双耳 4.现场录音 5.音视频通话 6.ai对话 7.离线翻译 8.超级翻译"
    )
    duration = fields.IntField(description="使用时长 s为单位")
    pos = fields.CharField(max_length=25, null=True, description="定位")
    time = fields.BigIntField(description="时间戳")
    platForm = fields.CharField(max_length=10, description="0.ios 1.安卓")
    version = fields.CharField(max_length=20, description="app版本")

    class Meta:
        table = "funcSummary"
        ordering = ["-time"]


class SmsRecord(Model):
    id = fields.IntField(pk=True)
    clientCode = fields.CharField(max_length=64)
    userid = fields.IntField()
    nationCode = fields.CharField(max_length=8)
    phoneNo = fields.CharField(max_length=16)
    content = fields.CharField(max_length=64)
    result = fields.BooleanField()
    time = fields.BigIntField()

    class Meta:
        table = "smsRecord"


class CallLogs(Model):
    id = fields.IntField(pk=True)
    caller_id = fields.CharField(max_length=255)
    receiver_id = fields.CharField(max_length=255)
    title = fields.CharField(max_length=50)
    status = fields.IntField()
    type = fields.IntField()
    duration = fields.IntField(null=True)
    caller_lan = fields.CharField(max_length=15, null=True)
    receiver_lan = fields.CharField(max_length=15, null=True)
    createtime = fields.BigIntField()

    class Meta:
        table = "call_logs"
        indexes = [("createtime",), ("caller_id", "receiver_id")]


class Friend(Model):
    id = fields.IntField(pk=True)
    caller_id = fields.CharField(max_length=255)
    receiver_id = fields.CharField(max_length=255)
    remark = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "friend"
        unique_together = (("caller_id", "receiver_id"),)


class BrandLimit(Model):
    id = fields.IntField(pk=True)
    brand_id = fields.IntField(description="品牌id")
    deepl = fields.BooleanField(description="是否启动deepl", default=False)
    super_translate = fields.BooleanField(description="是否启用超级翻译", default=True)
    offline_translate = fields.BooleanField(
        description="是否启用离线翻译", default=True
    )
    snap_translate = fields.BooleanField(description="是否启用拍照翻译", default=True)
    pip_translate = fields.BooleanField(description="是否启用画中画翻译", default=False)
    music = fields.BooleanField(description="是否启用音乐", default=False)
    audio_video = fields.BooleanField(description="是否启用音视频", default=True)
    dual_ear = fields.BooleanField(description="是否启用双耳", default=True)

    class Meta:
        table = "brand_limit"

    async def to_dict(self):
        return {
            "id": self.id,
            "brand_id": self.brand_id,
            "deepl": self.deepl,
            "super_translate": self.super_translate,
            "offline_translate": self.offline_translate,
            "snap_translate": self.snap_translate,
            "pip_translate": self.pip_translate,
            "music": self.music,
            "audio_video": self.audio_video,
            "dual_ear": self.dual_ear,
        }


class PipTranslation(Model):
    id = fields.IntField(pk=True)
    userid = fields.CharField(max_length=20, index=True)
    source_language = fields.CharField(max_length=20)
    target_language = fields.CharField(max_length=20)
    first_content = fields.CharField(max_length=50)
    content = fields.TextField()
    time = fields.BigIntField(description="时间戳")

    class Meta:
        table = "pip_translation"


class Admin(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=255)
    phone_no = fields.CharField(max_length=20, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True)
    last_login = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "admin"
        table_description = "管理员表"


class CsMessages(Model):
    id = fields.IntField(pk=True)
    userid = fields.CharField(max_length=32, description="用户id")
    message = fields.TextField(null=True, description="用户反馈信息")
    contact_info = fields.CharField(max_length=32, null=True, description="联系方式")
    file_url = fields.TextField(max_length=256, null=True, description="反馈文件地址")
    platform = fields.CharField(max_length=32, null=True, description="平台")
    version = fields.CharField(max_length=32, null=True, description="app版本")
    device_id = fields.CharField(max_length=256, null=True, description="设备id")
    brand = fields.CharField(max_length=32, null=True, description="手机品牌")
    active_code = fields.CharField(max_length=32, null=True, description="激活码")
    macaddr = fields.CharField(max_length=32, null=True, description="mac地址")
    question_type = fields.TextField(null=True, description="问题类型")
    repro_steps = fields.TextField(null=True, description="复现步骤")
    is_regression = fields.CharField(
        max_length=32, null=True, description="是否是回归问题"
    )
    issue_occur_time = fields.DatetimeField(null=True, description="问题发生时间")
    severity_level = fields.CharField(
        max_length=10, null=True, description="问题严重程度"
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    is_active = fields.BooleanField(default=True, description="是否有效")

    class Meta:
        table = "cs_messages"

    async def to_dict(self):
        return {
            "id": self.id,
            "userid": self.userid,
            "message": self.message,
            "contact_info": self.contact_info,
            "file_url": self.file_url,
            "platform": self.platform,
            "version": self.version,
            "device_id": self.device_id,
            "brand": self.brand,
            "active_code": self.active_code,
            "macaddr": self.macaddr,
            "question_type": self.question_type,
            "repro_steps": self.repro_steps,
            "is_regression": self.is_regression,
            "issue_occur_time": (
                self.issue_occur_time.strftime("%Y-%m-%d %H:%M:%S")
                if self.issue_occur_time
                else None
            ),
            "severity_level": self.severity_level,
            "create_time": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class RecordDurationDeduction(Model):
    id = fields.IntField(pk=True)
    duration_type = fields.CharField(max_length=20, description="功能类型", null=True)
    userid = fields.CharField(max_length=20, index=True)
    duration = fields.CharField(max_length=20, description="时长")
    is_free = fields.BooleanField(description="是否为免费时长")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "record_duration_deduction"

    async def to_dict(self):
        return {
            "id": self.id,
            "userid": self.userid,
            "duration_type": self.duration_type,
            "duration": self.duration,
            "is_free": self.is_free,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class MusicCategory(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64, unique=True, description="分类名称")
    icon = fields.CharField(max_length=256, null=True, description="分类图标 URL")
    sort_order = fields.IntField(default=0, description="展示排序，越大越靠前")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_at = fields.BigIntField(description="创建时间戳(ms)")
    updated_at = fields.BigIntField(description="更新时间戳(ms)")

    class Meta:
        table = "music_category"
        table_description = "音乐分类"
        indexes = [
            ("is_active", "sort_order"),
        ]
        ordering = ["-sort_order", "-id"]

    async def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Music(Model):
    id = fields.IntField(pk=True)
    category = fields.ForeignKeyField(
        "models.MusicCategory",
        related_name="music_list",
        description="所属分类",
        on_delete=fields.CASCADE,
    )
    title = fields.CharField(max_length=128, description="音乐标题")
    artist = fields.CharField(max_length=64, null=True, description="艺术家")
    cover_image = fields.CharField(max_length=256, null=True, description="封面图")
    audio_url = fields.CharField(max_length=256, description="音频地址")
    introduction = fields.TextField(null=True, description="音乐简介")
    duration = fields.IntField(description="时长，单位秒")
    is_vip = fields.BooleanField(default=False, description="是否 VIP 内容")
    play_count = fields.IntField(default=0, description="播放次数")
    sort_order = fields.IntField(default=0, description="展示排序")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_at = fields.BigIntField(description="创建时间戳(ms)")
    updated_at = fields.BigIntField(description="更新时间戳(ms)")

    class Meta:
        table = "music"
        table_description = "音乐内容"
        indexes = [
            ("category_id", "is_active"),
            ("is_vip", "is_active"),
            ("sort_order",),
        ]

    async def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category.id,
            "title": self.title,
            "artist": self.artist,
            "cover_image": self.cover_image,
            "audio_url": self.audio_url,
            "introduction": self.introduction,
            "duration": self.duration,
            "is_vip": self.is_vip,
            "play_count": self.play_count,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class UserMusicFavorites(Model):
    id = fields.IntField(pk=True)
    userid = fields.IntField(description="用户ID")
    music = fields.ForeignKeyField(
        "models.Music",
        related_name="favorite_users",
        description="收藏的音乐",
        on_delete=fields.CASCADE,
    )
    created_at = fields.BigIntField(description="收藏时间戳(ms)")

    class Meta:
        table = "user_music_favorites"
        table_description = "用户音乐收藏"
        unique_together = (("userid", "music_id"),)
        indexes = [
            ("userid", "created_at"),
        ]

    async def to_dict(self):
        return {
            "id": self.id,
            "userid": self.userid,
            "music_id": self.music.id,
            "created_at": self.created_at,
        }


class UserMacBinding(Model):
    id = fields.IntField(pk=True)
    userid = fields.IntField()
    clientid = fields.CharField(max_length=64)
    mac = fields.CharField(max_length=128)
    bind_time = fields.BigIntField()
    unbind_time = fields.BigIntField(default=0)

    class Meta:
        table = "user_mac_binding"
        indexes = [
            ("userid",),
            ("clientid", "mac"),
            ("clientid", "mac", "unbind_time"),
        ]

    async def to_dict(self):
        return {
            "id": self.id,
            "userid": self.userid,
            "clientid": self.clientid,
            "mac": self.mac,
            "bind_time": self.bind_time,
            "unbind_time": self.unbind_time,
        }


class Firmware(Model):
    id = fields.IntField(pk=True)
    firmware_id = fields.CharField(max_length=256)
    version = fields.CharField(max_length=32)
    description = fields.TextField(null=True)
    url = fields.CharField(max_length=256)
    is_active = fields.BooleanField(default=True)

