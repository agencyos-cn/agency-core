"""设备基类 - 所有硬件设备的抽象基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from dataclasses import dataclass, field
import asyncio

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """设备类型枚举"""
    LIGHT = "light"
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    ROBOT = "robot"
    WEARABLE = "wearable"  # 智能眼镜/耳机/手表
    CAMERA = "camera"
    SPEAKER = "speaker"
    MICROPHONE = "microphone"
    GATEWAY = "gateway"    # 网关设备（如 Home Assistant）


class DeviceStatus(Enum):
    """设备状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    SLEEP = "sleep"
    ERROR = "error"
    DISCOVERED = "discovered"  # 已发现但未连接


class CapabilityType(Enum):
    """能力类型枚举 - 参考 COSA 的技能库设计 [citation:2]"""
    # 感知能力
    VISION = "vision"               # 视觉感知（摄像头）
    AUDIO = "audio"                 # 音频感知（麦克风）
    TEMPERATURE = "temperature"     # 温度感知
    HUMIDITY = "humidity"           # 湿度感知
    MOTION = "motion"               # 运动感知（IMU）
    PROXIMITY = "proximity"         # 接近感知
    # 执行能力
    SWITCH = "switch"               # 开关控制
    DIMMER = "dimmer"               # 调光控制
    MOTOR = "motor"                 # 电机控制
    DISPLAY = "display"             # 显示输出
    SPEAK = "speak"                 # 语音输出
    # 复杂能力
    NAVIGATION = "navigation"       # 导航能力
    MANIPULATION = "manipulation"   # 操作能力（机械臂）
    MAPPING = "mapping"             # 建图能力


@dataclass
class DeviceCapability:
    """设备能力描述 - 每个技能都经过可靠性训练，支持独立迭代与组合调用 [citation:2]"""
    type: CapabilityType
    name: str
    version: str = "1.0.0"
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceInfo:
    """设备信息 - 参考 Agent Contract 概念 [citation:1]"""
    device_id: str
    name: str
    type: DeviceType
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    capabilities: List[DeviceCapability] = field(default_factory=list)
    connection_params: Dict[str, Any] = field(default_factory=dict)
    status: DeviceStatus = DeviceStatus.DISCOVERED


class BaseDevice(ABC):
    """所有设备的抽象基类"""
    def __init__(self, device_info: DeviceInfo):
        self.info = device_info
        self._connection = None
        self._callbacks = {}  # 事件回调函数
        self._lock = asyncio.Lock()
        logger.info(f"Device initialized: {device_info.name} ({device_info.device_id})")

    @abstractmethod
    async def connect(self) -> bool:
        """连接到设备"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """断开连接"""
        pass

    async def get_status(self) -> DeviceStatus:
        """获取设备状态"""
        return self.info.status

    def has_capability(self, capability_type: CapabilityType) -> bool:
        """检查是否具有某能力"""
        return any(cap.type == capability_type for cap in self.info.capabilities)

    def get_capability(self, capability_type: CapabilityType) -> Optional[DeviceCapability]:
        """获取指定类型的能力"""
        for cap in self.info.capabilities:
            if cap.type == capability_type:
                return cap
        return None

    async def execute(self, capability_type: CapabilityType, **params) -> Dict[str, Any]:
        """执行设备能力
        这是核心方法，对应 COSA 的技能调度机制 [citation:2]
        """
        if not self.has_capability(capability_type):
            raise ValueError(f"Device {self.info.device_id} does not support {capability_type}")
        
        async with self._lock:
            self.info.status = DeviceStatus.BUSY
            try:
                result = await self._execute_impl(capability_type, params)
                return result
            finally:
                self.info.status = DeviceStatus.ONLINE

    @abstractmethod
    async def _execute_impl(self, capability_type: CapabilityType, params: Dict) -> Dict[str, Any]:
        """实际执行能力（子类实现）"""
        pass

    def register_callback(self, event: str, callback):
        """注册事件回调"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    async def _trigger_event(self, event: str, data: Any):
        """触发事件"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)