"""设备抽象层模块"""
from .base import (
    BaseDevice, DeviceInfo, DeviceType, DeviceStatus, 
    CapabilityType, DeviceCapability
)
from .registry import DeviceRegistry
from .discovery import DeviceDiscovery, DiscoveryConfig, DiscoveryProtocol
from .connection import DeviceConnection, ConnectionConfig, ConnectionType, ConnectionStatus
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
    "DeviceConnection",
    "ConnectionConfig",
    "ConnectionType",
    "ConnectionStatus",
    "SmartLightDevice",
]
