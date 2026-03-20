"""邮件服务类 - 用于发送验证码等"""

import smtplib
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class MailService:
    def __init__(self):
        # 从环境变量中获取邮件配置
        self.smtp_server = os.getenv('MAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('MAIL_SMTP_PORT', 587))
        self.sender_email = os.getenv('MAIL_USERNAME', '')
        self.sender_password = os.getenv('MAIL_PASSWORD', '')
        self.use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        
        # 存储验证码的临时字典，实际生产环境应使用Redis等
        self.verification_codes = {}

    def send_verification_code(self, recipient_email: str, subject: str = "密码重置验证码") -> str:
        """发送验证码到指定邮箱"""
        # 生成6位数字验证码
        code = str(random.randint(100000, 999999))
        self.verification_codes[recipient_email] = code

        # 创建邮件内容
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        body = f"您的验证码是: {code}\n此验证码将在10分钟后失效。"
        msg.attach(MIMEText(body, 'plain'))

        try:
            # 连接到SMTP服务器并发送邮件
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.ehlo()
            
            if self.use_tls:
                server.starttls()
                server.ehlo()
                
            server.login(self.sender_email, self.sender_password)
            
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()
            
            print(f"验证码已发送到 {recipient_email}")
            return code
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP认证失败: {e}")
            raise Exception(f"SMTP认证失败，请检查邮箱用户名和密码: {e}")
        except smtplib.SMTPConnectError as e:
            print(f"SMTP连接失败: {e}")
            raise Exception(f"无法连接到SMTP服务器，请检查服务器设置: {e}")
        except smtplib.SMTPRecipientsRefused as e:
            print(f"收件人邮箱被拒绝: {e}")
            raise Exception(f"收件人邮箱地址无效: {e}")
        except Exception as e:
            print(f"发送邮件失败: {e}")
            raise Exception(f"发送邮件失败: {str(e)}")

    def verify_code(self, email: str, code: str) -> bool:
        """验证验证码是否正确"""
        if email not in self.verification_codes:
            return False
            
        stored_code = self.verification_codes[email]
        # 验证码使用后即失效
        del self.verification_codes[email]
        return stored_code == code