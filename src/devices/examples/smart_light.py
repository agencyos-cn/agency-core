"""示例：智能灯泡设备"""
import asyncio
from typing import Dict, Any
import logging
from ..base import BaseDevice, DeviceInfo, DeviceType, DeviceCapability, CapabilityType, DeviceStatus

logger = logging.getLogger(__name__)

class SmartLightDevice(BaseDevice):
    """智能灯泡设备示例"""
    
    def __init__(self, device_id: str, name: str, connection_params: Dict = None):
        # 定义设备能力
        capabilities = [
            DeviceCapability(
                type=CapabilityType.SWITCH,
                name="电源开关",
                parameters={"state": {"type": "boolean", "description": "true=开, false=关"}}
            ),
            DeviceCapability(
                type=CapabilityType.DIMMER,
                name="亮度调节",
                version="1.1.0",
                parameters={"brightness": {"type": "integer", "min": 0, "max": 100}}
            )
        ]
        
        device_info = DeviceInfo(
            device_id=device_id,
            name=name,
            type=DeviceType.LIGHT,
            manufacturer="Example Corp",
            model="SmartBulb v1",
            capabilities=capabilities,
            connection_params=connection_params or {},
            status=DeviceStatus.DISCOVERED
        )
        
        super().__init__(device_info)
        
        # 设备内部状态
        self._power_on = False
        self._brightness = 50
    
    async def connect(self) -> bool:
        """模拟连接设备"""
        logger.info(f"Connecting to smart light {self.info.name}...")
        await asyncio.sleep(0.5)  # 模拟连接耗时
        self.info.status = DeviceStatus.ONLINE
        logger.info(f"Connected to {self.info.name}")
        return True
    
    async def disconnect(self) -> bool:
        """模拟断开连接"""
        logger.info(f"Disconnecting from {self.info.name}...")
        self.info.status = DeviceStatus.OFFLINE
        return True
    
    async def _execute_impl(self, capability_type: CapabilityType, params: Dict) -> Dict[str, Any]:
        """执行设备能力"""
        if capability_type == CapabilityType.SWITCH:
            state = params.get("state")
            if state is not None:
                self._power_on = state
                return {
                    "success": True,
                    "state": self._power_on,
                    "message": f"Light turned {'on' if self._power_on else 'off'}"
                }
            return {"success": False, "message": "Missing state parameter"}
            
        elif capability_type == CapabilityType.DIMMER:
            brightness = params.get("brightness")
            if brightness is not None and 0 <= brightness <= 100:
                self._brightness = brightness
                return {
                    "success": True,
                    "brightness": self._brightness,
                    "message": f"Brightness set to {brightness}%"
                }
            return {"success": False, "message": "Invalid brightness value (0-100)"}
            
        return {"success": False, "message": "Invalid parameters"}
    
    async def get_state(self) -> Dict[str, Any]:
        """获取当前状态（自定义方法）"""
        return {
            "power_on": self._power_on,
            "brightness": self._brightness
        }