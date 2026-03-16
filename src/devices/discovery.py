# src/devices/discovery.py
"""设备发现模块 - 支持多种协议发现"""

import asyncio
import socket
import json
from typing import Dict, List, Optional, Callable, Awaitable
from dataclasses import dataclass
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class DiscoveryProtocol(Enum):
    """发现协议类型"""
    MDNS = "mdns"           # 多播DNS
    BLE = "ble"             # 蓝牙
    UDP = "udp"             # UDP广播
    HTTP = "http"           # HTTP端点
    MQTT = "mqtt"           # MQTT发现


@dataclass
class DiscoveryConfig:
    """发现配置"""
    protocols: List[DiscoveryProtocol]
    timeout: int = 5
    filters: Dict[str, str] = None


class DeviceDiscovery:
    """设备发现管理器"""
    
    def __init__(self):
        self._discovered_devices = {}
        self._discovery_tasks = []
        self._listeners = []
    
    async def start_discovery(self, config: DiscoveryConfig):
        """启动设备发现"""
        logger.info(f"Starting device discovery with protocols: {config.protocols}")
        
        tasks = []
        for protocol in config.protocols:
            if protocol == DiscoveryProtocol.MDNS:
                tasks.append(self._discover_mdns(config.timeout))
            elif protocol == DiscoveryProtocol.BLE:
                tasks.append(self._discover_ble(config.timeout))
            elif protocol == DiscoveryProtocol.UDP:
                tasks.append(self._discover_udp(config.timeout))
            elif protocol == DiscoveryProtocol.HTTP:
                tasks.append(self._discover_http(config.timeout))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Discovery error: {result}")
            elif result:
                for device_info in result:
                    self._discovered_devices[device_info['device_id']] = device_info
                    await self._notify_listeners(device_info)
        
        return list(self._discovered_devices.values())
    
    async def _discover_mdns(self, timeout: int) -> List[Dict]:
        """mDNS发现（模拟实现）"""
        # TODO: 使用 zeroconf 或 avahi 实现
        await asyncio.sleep(0.1)
        return []
    
    async def _discover_ble(self, timeout: int) -> List[Dict]:
        """蓝牙发现（模拟实现）"""
        # TODO: 使用 bleak 实现
        await asyncio.sleep(0.1)
        return []
    
    async def _discover_udp(self, timeout: int) -> List[Dict]:
        """UDP广播发现"""
        devices = []
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)
        
        # 发送发现广播
        broadcast_msg = json.dumps({"type": "DISCOVER", "version": "1.0"}).encode()
        sock.sendto(broadcast_msg, ('<broadcast>', 18789))  # OpenClaw 默认端口
        
        # 接收响应
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                data, addr = sock.recvfrom(1024)
                device_info = json.loads(data.decode())
                device_info['ip'] = addr[0]
                devices.append(device_info)
                logger.debug(f"Discovered device via UDP: {device_info}")
            except socket.timeout:
                break
            except Exception as e:
                logger.error(f"UDP discovery error: {e}")
        
        sock.close()
        return devices
    
    async def _discover_http(self, timeout: int) -> List[Dict]:
        """HTTP端点发现"""
        # TODO: 实现 HTTP 发现
        return []
    
    def add_listener(self, callback: Callable[[Dict], Awaitable[None]]):
        """添加发现监听器"""
        self._listeners.append(callback)
    
    async def _notify_listeners(self, device_info: Dict):
        """通知所有监听器"""
        for listener in self._listeners:
            try:
                await listener(device_info)
            except Exception as e:
                logger.error(f"Listener error: {e}")