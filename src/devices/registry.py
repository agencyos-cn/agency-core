# src/devices/registry.py
"""设备注册表 - 管理所有已发现/连接的设备"""

from typing import Dict, Optional, List
import asyncio
import logging
from .base import BaseDevice, DeviceInfo, DeviceStatus

logger = logging.getLogger(__name__)

class DeviceRegistry:
    """设备注册表 - 管理设备生命周期"""
    
    def __init__(self):
        self._devices: Dict[str, BaseDevice] = {}  # device_id -> device
        self._device_info: Dict[str, DeviceInfo] = {}  # device_id -> info
        self._status_callbacks = []
    
    def register_device(self, device: BaseDevice):
        """注册设备"""
        self._devices[device.info.device_id] = device
        self._device_info[device.info.device_id] = device.info
        logger.info(f"Device registered: {device.info.name} ({device.info.device_id})")
    
    def unregister_device(self, device_id: str):
        """注销设备"""
        if device_id in self._devices:
            del self._devices[device_id]
        if device_id in self._device_info:
            del self._device_info[device_id]
        logger.info(f"Device unregistered: {device_id}")
    
    def get_device(self, device_id: str) -> Optional[BaseDevice]:
        """获取设备实例"""
        return self._devices.get(device_id)
    
    def get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """获取设备信息"""
        return self._device_info.get(device_id)
    
    def list_devices(self, status: Optional[DeviceStatus] = None) -> List[DeviceInfo]:
        """列出设备"""
        if status:
            return [info for info in self._device_info.values() if info.status == status]
        return list(self._device_info.values())
    
    def find_devices_by_capability(self, capability_type) -> List[DeviceInfo]:
        """按能力查找设备"""
        devices = []
        for device_id, device in self._devices.items():
            if device.has_capability(capability_type):
                devices.append(self._device_info[device_id])
        return devices
    
    async def update_device_status(self, device_id: str, status: DeviceStatus):
        """更新设备状态"""
        if device_id in self._device_info:
            self._device_info[device_id].status = status
            await self._notify_status_change(device_id, status)
    
    def add_status_callback(self, callback):
        """添加状态变更回调"""
        self._status_callbacks.append(callback)
    
    async def _notify_status_change(self, device_id: str, status: DeviceStatus):
        """通知状态变更"""
        for callback in self._status_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(device_id, status)
                else:
                    callback(device_id, status)
            except Exception as e:
                logger.error(f"Status callback error: {e}")