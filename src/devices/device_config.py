"""Device Configuration"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import json


@dataclass
class DeviceConfig:
    """设备配置"""
    # 发现配置
    discovery_enabled: bool = True  # 添加缺失的字段
    supported_protocols: List[str] = None  # 添加缺失的字段
    reconnect_interval: int = 5  # 添加缺失的字段
    
    # 通用设备配置
    scan_interval: int = 30  # seconds
    connection_timeout: int = 10  # seconds
    retry_attempts: int = 3
    max_connections: int = 50
    
    # 发现配置
    enable_discovery: bool = True
    discovery_methods: List[str] = None  # ['mdns', 'ble', 'udp', 'http']
    discovery_timeout: int = 10  # seconds
    
    # 设备认证配置
    auth_required: bool = True
    auth_timeout: int = 5  # seconds
    
    # 连接配置
    connection_pool_size: int = 10
    keep_alive: bool = True
    keep_alive_interval: int = 60  # seconds
    
    # 安全配置
    allow_untrusted_certs: bool = False
    encryption_enabled: bool = True
    
    # 设备特定配置
    device_specific_configs: Dict[str, Any] = None
    
    # 设备注册表配置
    device_registry: Dict[str, Any] = None  # 添加缺失的字段
    
    def __post_init__(self):
        if self.supported_protocols is None:
            self.supported_protocols = ["tcp", "udp", "mqtt", "http", "websocket"]
        if self.discovery_methods is None:
            self.discovery_methods = ['mdns', 'ble', 'udp', 'http']
        if self.device_specific_configs is None:
            self.device_specific_configs = {}
        if self.device_registry is None:
            self.device_registry = {"type": "memory", "config": {}}


@dataclass
class DeviceConnectionConfig:
    """设备连接配置"""
    device_id: str
    connection_type: str  # tcp, udp, websocket, http, https, mqtt, ble
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    timeout: float = 5.0
    keepalive: bool = False
    ssl_verify: bool = True
    username: Optional[str] = None
    password: Optional[str] = None
    extra_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}