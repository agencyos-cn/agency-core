"""邮件配置"""

import os
from dataclasses import dataclass


def _get_int_env(env_var: str, default: int) -> int:
    """从环境变量获取整数值，如果环境变量为空或不存在则返回默认值"""
    value = os.getenv(env_var, "")
    if value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass
class MailConfig:
    """邮件配置"""
    smtp_server: str = os.getenv("MAIL_SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = None  # 使用None作为默认值，稍后在初始化时设置
    sender_email: str = os.getenv("MAIL_SENDER_EMAIL", "")
    sender_password: str = os.getenv("MAIL_SENDER_PASSWORD", "")
    mail_use_tls: bool = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    
    def __post_init__(self):
        if self.smtp_port is None:
            self.smtp_port = _get_int_env("MAIL_SMTP_PORT", 587)