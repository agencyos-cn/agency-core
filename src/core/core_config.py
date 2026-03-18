"""核心运行时配置"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CoreConfig:
    """核心运行时配置项"""
    # 服务基本信息
    service_name: str = "AgencyOS-Core"        # 服务名称
    host: str = "0.0.0.0"                     # 服务监听地址
    port: int = 18789                         # 服务监听端口
    debug: bool = False                       # 是否开启调试模式
    
    # 第三方生态集成配置
    enable_third_party_ecosystem: bool = True  # 启用第三方生态
    ecosystem_sync_interval: int = 1800       # 生态同步间隔（秒）
    
    # 外部服务集成
    external_services: Optional[Dict[str, Any]] = None  # 外部服务配置
    enable_service_discovery: bool = True      # 启用服务发现
    
    # 缓存配置
    cache_enabled: bool = True                 # 启用缓存
    cache_ttl: int = 3600                     # 缓存生存时间
    cache_backend: str = "memory"              # 缓存后端 (memory, redis, etc.)
    
    # 日志配置
    log_level: str = "INFO"                    # 日志级别
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None             # 日志文件路径


# 默认配置
DEFAULT_CORE_CONFIG = CoreConfig(
    service_name="AgencyOS-Core",
    host="0.0.0.0",
    port=18789,
    debug=False,
    external_services={},
)