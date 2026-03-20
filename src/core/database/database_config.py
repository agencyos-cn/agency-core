"""Database Configuration"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """数据库配置"""
    # 数据库连接配置
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "3306"))
    user: str = os.getenv("DB_USER", "")
    password: str = os.getenv("DB_PASSWORD", "")
    database: str = os.getenv("DB_NAME", "")
    charset: str = os.getenv("DB_CHARSET", "utf8mb4")
    
    # 连接池配置
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour
    
    # 连接超时配置
    connect_timeout: int = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))  # 秒
    read_timeout: int = int(os.getenv("DB_READ_TIMEOUT", "10"))  # 秒
    write_timeout: int = int(os.getenv("DB_WRITE_TIMEOUT", "10"))  # 秒
    
    # SSL配置
    ssl_enabled: bool = os.getenv("DB_SSL_ENABLED", "false").lower() == "true"
    ssl_ca: Optional[str] = os.getenv("DB_SSL_CA", None)
    ssl_cert: Optional[str] = os.getenv("DB_SSL_CERT", None)
    ssl_key: Optional[str] = os.getenv("DB_SSL_KEY", None)
    
    # 其他选项
    autocommit: bool = os.getenv("DB_AUTOCOMMIT", "false").lower() == "true"
    use_unicode: bool = os.getenv("DB_USE_UNICODE", "true").lower() == "true"
    
    def get_connection_params(self):
        """获取连接参数字典"""
        params = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'charset': self.charset,
            'connect_timeout': self.connect_timeout,
            'read_timeout': self.read_timeout,
            'write_timeout': self.write_timeout
        }
        
        if self.ssl_enabled:
            params['ssl'] = {
                'ca': self.ssl_ca,
                'cert': self.ssl_cert,
                'key': self.ssl_key
            }
        
        return params