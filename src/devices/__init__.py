"""Devices module for AgencyOS"""

from .base import BaseDevice, DeviceInfo, DeviceCapability, DeviceType, CapabilityType, DeviceStatus
from .registry import DeviceRegistry
from .discovery import DeviceDiscovery, DiscoveryConfig, DiscoveryProtocol
from .connection import DeviceConnection, ConnectionConfig, ConnectionType, ConnectionStatus
from .device_config import DeviceConfig, DeviceConnectionConfig

# 导入示例设备
from .examples.smart_light import SmartLightDevice

__all__ = [
    "BaseDevice",
    "DeviceInfo", 
    "DeviceCapability",
    "DeviceType",
    "CapabilityType",
    "DeviceStatus",
    "DeviceRegistry",
    "DeviceDiscovery", 
    "DeviceConnection",
    "ConnectionConfig",
    "ConnectionType",
    "ConnectionStatus",
    "DeviceConfig",
    "DeviceConnectionConfig",
    "SmartLightDevice",
    "DiscoveryConfig",
    "DiscoveryProtocol"
]