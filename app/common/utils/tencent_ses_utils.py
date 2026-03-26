from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import aiosmtplib
import smtplib

from app.core.config import settings
from app.common.utils.log_utils import log_util

logger = log_util.get_logger("tencent_ses_utils")


class TencentSES:
    def __init__(self):
        self.sender = settings.email_sender
        self.sender_alias = settings.email_sender_alias
        self.sender_pwd = settings.smtp_password
        self.host = settings.smtp_host
        self.port = settings.smtp_port

    async def send_verification_code(self, user_email, code):
        try:
            subject = "VoxiGo Verification Code"

            content = f"""
            <html>
                <body>
                    <h3>Your verification code:</h3>
                    <div style="font-size:24px; color:#1890ff;">{code}</div>
                    <p>This code expires in 5 minutes. Please do not share it with others.</p>
                </body>
            </html>
            """

            # 构造邮件
            message = MIMEMultipart('alternative')
            mime_text = MIMEText(content, _subtype='html', _charset='UTF-8')
            message["Subject"] = Header(subject, "utf-8")
            sender_alias = self.sender_alias
            sender = self.sender
            message['From'] = formataddr((sender_alias, sender))
            message["To"] = ", ".join([user_email])
            message.attach(mime_text)

            async with aiosmtplib.SMTP(hostname=self.host, port=self.port, use_tls=True) as server:
                await server.login(self.sender, self.sender_pwd)
                await server.send_message(message)
            logger.info(f"邮件发送成功 | to={user_email} | code={code}")
            return {"success": True, "message": "邮件发送成功"}

        except smtplib.SMTPException as e:
            logger.error(f"邮件发送失败 | to={user_email} | error={str(e)}")
            return {"success": False, "message": f"邮件发送失败: {str(e)}"}
        except Exception as e:
            logger.error(f"邮件发送失败 | to={user_email} | error={str(e)}")
            return {"success": False, "message": f"系统错误: {str(e)}"}
