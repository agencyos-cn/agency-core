"""设备抽象层模块"""
from .base import (
    BaseDevice,
    DeviceInfo,
    DeviceType,
    DeviceStatus,
    CapabilityType,
    DeviceCapability,
)
from .registry import DeviceRegistry
from .discovery import (
    DeviceDiscovery,
    DiscoveryConfig,
    DiscoveryProtocol,
)
# 从 .connection import DeviceConnection  # 稍后实现
from .examples.smart_light import SmartLightDevice

__all__ = [
    "BaseDevice",
    "DeviceInfo",
    "DeviceType",
    "DeviceStatus",
    "CapabilityType",
    "DeviceCapability",
    "DeviceRegistry",
    "DeviceDiscovery",
    "DiscoveryConfig",
    "DiscoveryProtocol",
    "SmartLightDevice",
]
