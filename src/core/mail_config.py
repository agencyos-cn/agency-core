"""邮件配置"""

import os
from dataclasses import dataclass


@dataclass
class MailConfig:
    """邮件配置"""
    smtp_server: str = os.getenv("MAIL_SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("MAIL_SMTP_PORT", "587"))
    sender_email: str = os.getenv("MAIL_SENDER_EMAIL", "")
    sender_password: str = os.getenv("MAIL_SENDER_PASSWORD", "")
    mail_use_tls: bool = os.getenv("MAIL_USE_TLS", "true").lower() == "true"