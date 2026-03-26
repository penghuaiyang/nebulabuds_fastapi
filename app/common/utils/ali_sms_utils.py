import json
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_tea_util.client import Client as UtilClient
from app.common import log_util
from app.core.config import settings
logger = log_util.get_logger("sms")


class AliSMS:
    def __init__(self):
        pass

    async def create_client(
            access_key_id: str,
            access_key_secret: str,
    ) -> Dysmsapi20170525Client:

        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        config.endpoint = settings.aliyun_sms_endpoint
        return Dysmsapi20170525Client(config)

    @staticmethod
    async def send_sms(phone_no, code):
        client = await AliSMS.create_client(
            settings.aliyun_sms_access_key_id,
            settings.aliyun_sms_access_key_secret,
        )
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            sign_name=settings.aliyun_sms_sign_name,
            template_code=settings.aliyun_sms_template_code,
            phone_numbers=phone_no,
            template_param=json.dumps({"code": code})
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.send_sms_with_options(send_sms_request, runtime)
            ConsoleClient.log(UtilClient.to_jsonstring(resp))
            code = resp.body.code
            message = resp.body.message
            if code == 'OK':
                logger.info(f"短信发送成功 | to={phone_no} | code={code}")
                return 1, message
            else:
                logger.error(f"短信发送失败 | to={phone_no} | error={message}")
                return 0, message

        except Exception as error:
            logger.error(f"短信发送失败 | to={phone_no} | error={str(error)}")
            return -1, "未知错误"
