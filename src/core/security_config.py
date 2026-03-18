"""Security Configuration"""

import os
from dataclasses import dataclass
from typing import Optional, List
import secrets


@dataclass
class SecurityConfig:
    """安全配置"""
    # 加密启用标志
    encryption_enabled: bool = True
    # 从环境变量获取加密密钥，如果不存在则生成一个默认的（仅用于开发）
    # 推荐使用至少32字节(256位)的随机密钥
    encryption_key: str = os.getenv("ENCRYPTION_KEY", secrets.token_urlsafe(32))  # 用于JWT签名的密钥
    
    # 访问控制
    access_control_enabled: bool = True
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 100
    
    # SSL配置
    ssl_enabled: bool = False
    ssl_cert_file: str = ""
    ssl_key_file: str = ""
    
    # API密钥管理
    enforce_api_key_validation: bool = True
    api_key_storage_encrypted: bool = True
    api_key_expiry_days: int = 30
    
    # 访问控制
    enable_rbac: bool = True  # Role-Based Access Control
    default_user_role: str = "user"
    allowed_origins: List[str] = None  # For CORS
    
    # 数据加密
    encrypt_sensitive_data: bool = True
    encryption_algorithm: str = "Fernet"  # Using cryptography.fernet
    encryption_key_path: Optional[str] = None
    
    # 审计日志
    enable_audit_logging: bool = True
    audit_log_retention_days: int = 90
    
    # 速率限制
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 100  # per minute
    rate_limit_window: int = 60  # seconds
    
    # 输入验证
    enable_input_sanitization: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    
    # 安全头
    enable_security_headers: bool = True
    
    # 安全扫描
    enable_vulnerability_scanning: bool = False
    
    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["http://localhost", "http://127.0.0.1"]