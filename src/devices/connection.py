"""设备连接管理模块-处理与设备的通信连接"""
import asyncio
import socket
import json
from typing import Dict, Any, Optional, Callable, Union, NamedTuple
import logging
from enum import Enum
from dataclasses import dataclass, field
import ssl

logger = logging.getLogger(__name__)

# 连接状态枚举
class ConnectionStatus(Enum):
    """连接状态"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    CLOSED = "closed"

class ConnectionType(Enum):
    """连接类型"""
    TCP = "tcp"
    UDP = "udp"
    WEBSOCKET = "websocket"
    SERIAL = "serial"
    BLE = "ble"
    MQTT = "mqtt"
    HTTP = "http"
    HTTPS = "https"

# TCP连接对象
class TCPConnection(NamedTuple):
    """TCP连接对象"""
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

# 类型别名
MessageCallback = Callable[[bytes], Any]
ErrorCallback = Callable[[Exception], Any]
StatusCallback = Callable[[ConnectionStatus], Any]
ConnectionObject = Union[TCPConnection, 'asyncio.DatagramTransport', Any]

@dataclass
class ConnectionConfig:
    """连接配置"""
    connection_type: ConnectionType
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None  # WebSocket/HTTP路径
    timeout: float = 5.0
    retry_count: int = 3
    retry_delay: float = 1.0
    keepalive: bool = False
    ssl_verify: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    auth: Optional[Dict[str, str]] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)
    reconnect_backoff: float = 1.0  # 重连退避时间
    reconnect_max_backoff: float = 60.0  # 最大退避时间

class ConnectionError(Exception):
    """连接异常"""
    pass

class DeviceConnection:
    """设备连接管理器
    负责与物理设备的通信连接管理，支持多种协议：
    - TCP/UDP 套接字连接
    - WebSocket 长连接
    - HTTP/HTTPS REST API
    - 串口通信（待实现）
    - BLE（待实现）
    - MQTT（待实现）
    """
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._connection: Optional[ConnectionObject] = None
        self._status = ConnectionStatus.DISCONNECTED
        self._receive_task = None
        self._ping_task = None
        self._reconnect_count = 0
        self._message_callback: Optional[MessageCallback] = None
        self._error_callback: Optional[ErrorCallback] = None
        self._status_callback: Optional[StatusCallback] = None
        self._lock = asyncio.Lock()
        self._receive_buffer = bytearray()
        
        logger.debug(f"Connection initialized: {config.connection_type}://{config.host}:{config.port}{config.path or ''}")

    @property
    def status(self) -> ConnectionStatus:
        """获取当前连接状态"""
        return self._status

    async def connect(self) -> bool:
        """建立连接"""
        async with self._lock:
            if self._status == ConnectionStatus.CONNECTED:
                logger.warning("Already connected")
                return True
                
            self._status = ConnectionStatus.CONNECTING
            await self._trigger_status_change()
            
            try:
                logger.info(f"Connecting to {self.config.connection_type.value}://{self.config.host}:{self.config.port}...")
                
                if self.config.connection_type == ConnectionType.TCP:
                    await self._connect_tcp()
                elif self.config.connection_type == ConnectionType.UDP:
                    await self._connect_udp()
                elif self.config.connection_type == ConnectionType.WEBSOCKET:
                    await self._connect_websocket()
                elif self.config.connection_type in [ConnectionType.HTTP, ConnectionType.HTTPS]:
                    # HTTP是短连接，不需要保持长连接
                    self._status = ConnectionStatus.CONNECTED
                else:
                    raise ConnectionError(f"Unsupported connection type: {self.config.connection_type}")
                
                self._status = ConnectionStatus.CONNECTED
                self._reconnect_count = 0
                logger.info(f"Connected successfully to {self.config.host}:{self.config.port}")
                await self._trigger_status_change()
                
                # 如果开启了 keepalive，启动心跳任务
                if self.config.keepalive:
                    self._start_keepalive()
                    
                return True
                
            except Exception as e:
                self._status = ConnectionStatus.ERROR
                logger.error(f"Connection failed: {e}")
                await self._trigger_status_change()
                
                if self._error_callback:
                    await self._safe_callback(self._error_callback, e)
                
                # 尝试重连
                if self._reconnect_count < self.config.retry_count:
                    self._reconnect_count += 1
                    # 指数退避：1s, 2s, 4s, 8s...
                    wait_time = min(
                        self.config.reconnect_backoff * (2 ** (self._reconnect_count - 1)),
                        self.config.reconnect_max_backoff
                    )
                    logger.info(f"Retrying connection in {wait_time:.1f}s ({self._reconnect_count}/{self.config.retry_count})...")
                    await asyncio.sleep(wait_time)
                    return await self.connect()
                
                return False

    async def _connect_tcp(self):
        """建立 TCP 连接"""
        try:
            # 只对HTTPS连接启用SSL
            if self.config.connection_type == ConnectionType.HTTPS:
                # 创建SSL上下文
                ssl_context = ssl.create_default_context()
                if not self.config.ssl_verify:
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
                reader, writer = await asyncio.open_connection(
                    host=self.config.host,
                    port=self.config.port,
                    ssl=ssl_context,
                    ssl_handshake_timeout=self.config.timeout
                )
            else:
                # 普通TCP连接不使用SSL
                reader, writer = await asyncio.open_connection(
                    host=self.config.host,
                    port=self.config.port
                )
            
            self._connection = TCPConnection(reader=reader, writer=writer)
            
            self._receive_task = asyncio.create_task(self._tcp_receive_loop())
        except Exception as e:
            raise ConnectionError(
                f"TCP connection failed to {self.config.host}:{self.config.port}: {e}"
            ) from e

    async def _tcp_receive_loop(self):
        """TCP 接收循环"""
        if not isinstance(self._connection, TCPConnection):
            logger.error("TCP receive loop: invalid connection type")
            return
            
        reader = self._connection.reader
        
        try:
            while self._status == ConnectionStatus.CONNECTED:
                try:
                    data = await asyncio.wait_for(
                        reader.read(1024),
                        timeout=self.config.timeout
                    )
                    
                    if not data:
                        logger.debug("TCP connection closed by peer")
                        break
                        
                    if self._message_callback:
                        await self._safe_callback(self._message_callback, data)
                        
                except asyncio.TimeoutError:
                    # 超时是正常的，继续循环
                    continue
                except Exception as e:
                    logger.error(f"TCP receive error: {e}")
                    break
                    
        except asyncio.CancelledError:
            logger.debug("TCP receive task cancelled")
        finally:
            if self._status == ConnectionStatus.CONNECTED:
                await self.disconnect()

    async def _connect_udp(self):
        """建立 UDP 连接"""
        try:
            class UDPProtocol(asyncio.DatagramProtocol):
                def __init__(self, connection):
                    self.connection = connection
                    self.transport = None
                    
                def connection_made(self, transport):
                    self.transport = transport
                    
                def datagram_received(self, data, addr):
                    if self.connection._message_callback:
                        asyncio.create_task(
                            self.connection._safe_callback(
                                self.connection._message_callback, data
                            )
                        )
                        
                def error_received(self, exc):
                    if self.connection._error_callback:
                        asyncio.create_task(
                            self.connection._safe_callback(
                                self.connection._error_callback, exc
                            )
                        )

            loop = asyncio.get_running_loop()
            
            # 检查host和port是否有效
            if not self.config.host or not self.config.port:
                raise ConnectionError("UDP connection requires both host and port")
                
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: UDPProtocol(self),
                remote_addr=(self.config.host, self.config.port)
            )
            
            self._connection = transport
            
        except Exception as e:
            raise ConnectionError(
                f"UDP connection failed to {self.config.host}:{self.config.port}: {e}"
            ) from e

    async def _connect_websocket(self):
        """建立 WebSocket 连接"""
        try:
            import websockets
            
            # 构建 WebSocket URI
            protocol = "wss" if self.config.ssl_verify else "ws"
            uri = f"{protocol}://{self.config.host}:{self.config.port}{self.config.path or ''}"
            
            # 设置额外头信息
            extra_headers = self.config.headers.copy()
            
            # 根据 websockets 版本处理参数
            connect_kwargs = {
                'ping_interval': None if not self.config.keepalive else 30,
                'ping_timeout': self.config.timeout,
                'close_timeout': self.config.timeout
            }
            
            # 尝试使用额外的头部参数
            try:
                self._connection = await websockets.connect(
                    uri,
                    additional_headers=extra_headers,
                    **connect_kwargs
                )
            except TypeError:
                # 如果 additional_headers 不被支持，尝试使用 extra_headers
                try:
                    self._connection = await websockets.connect(
                        uri,
                        extra_headers=extra_headers,
                        **connect_kwargs
                    )
                except TypeError:
                    # 如果都不支持，不带额外头部连接
                    self._connection = await websockets.connect(
                        uri,
                        **connect_kwargs
                    )
            
            self._receive_task = asyncio.create_task(self._websocket_receive_loop())
            
        except ImportError:
            raise ConnectionError("websockets library not installed. Run: pip install websockets")
        except Exception as e:
            # 明确区分是导入错误还是连接错误
            if "websockets" not in str(type(e).__name__) and "ImportError" not in str(type(e).__name__):
                raise ConnectionError(
                    f"WebSocket connection failed to {self.config.host}:{self.config.port}. "
                    f"The websockets library is available but connection failed: {e}"
                ) from e
            else:
                raise ConnectionError(
                    f"WebSocket connection failed to {self.config.host}:{self.config.port}: {e}"
                ) from e

    async def _websocket_receive_loop(self):
        """WebSocket 接收循环"""
        try:
            # 确保连接存在且是websockets连接
            if (self._connection and 
                self.config.connection_type == ConnectionType.WEBSOCKET):
                websocket_conn = self._connection
                async for message in websocket_conn:
                    if self._message_callback:
                        data = message if isinstance(message, bytes) else message.encode()
                        await self._safe_callback(self._message_callback, data)
            else:
                logger.error("WebSocket receive loop: no active connection")
                    
        except Exception as e:
            # 检查是否是连接关闭异常
            if 'ConnectionClosed' in str(type(e)):
                logger.debug("WebSocket connection closed")
            else:
                logger.error(f"WebSocket receive error: {e}")
        finally:
            if self._status == ConnectionStatus.CONNECTED:
                await self.disconnect()

    async def send(self, data: Union[str, bytes, dict]) -> bool:
        """发送数据
        Args:
            data: 要发送的数据（字符串、字节或字典）
        Returns:
            发送是否成功
        """
        if self._status != ConnectionStatus.CONNECTED:
            logger.error("Cannot send: not connected")
            return False
            
        try:
            # 准备数据
            if isinstance(data, dict):
                data = json.dumps(data)
                
            if isinstance(data, str):
                data = data.encode('utf-8')
                
            if self.config.connection_type == ConnectionType.TCP:
                if isinstance(self._connection, TCPConnection):
                    self._connection.writer.write(data)
                    await self._connection.writer.drain()
                else:
                    logger.error("TCP send: invalid connection type")
                    return False
            elif self.config.connection_type == ConnectionType.UDP:
                if self._connection and hasattr(self._connection, 'sendto'):
                    # 对UDP连接使用sendto方法
                    self._connection.sendto(data)
                else:
                    logger.error("UDP send: invalid connection type")
                    return False
            elif self.config.connection_type == ConnectionType.WEBSOCKET:
                if self._connection and hasattr(self._connection, 'send'):
                    # 对WebSocket连接使用send方法
                    await self._connection.send(data)
                else:
                    logger.error("WebSocket send: invalid connection type")
                    return False
            elif self.config.connection_type in [ConnectionType.HTTP, ConnectionType.HTTPS]:
                # HTTP 短连接，每次发送单独处理
                return await self._http_request(data)
                
            return True
            
        except Exception as e:
            logger.error(f"Send failed: {e}")
            
            if self._error_callback:
                await self._safe_callback(self._error_callback, e)
                
            return False

    async def _http_request(self, data: Union[str, bytes, dict]) -> bool:
        """发送 HTTP 请求
        
        Args:
            data: 要发送的数据（字符串、字节或字典）
            
        Returns:
            发送是否成功
        """
        try:
            import aiohttp
            
            # 数据预处理和类型检查
            if isinstance(data, dict):
                data_bytes = json.dumps(data).encode('utf-8')
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
            elif isinstance(data, bytes):
                data_bytes = data
            else:
                logger.error(f"Unsupported data type for HTTP request: {type(data)}")
                return False
                
            protocol = "https" if self.config.connection_type == ConnectionType.HTTPS else "http"
            url = f"{protocol}://{self.config.host}:{self.config.port}{self.config.path or ''}"
            
            headers = self.config.headers.copy()
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
                
            # 创建SSL上下文（如果需要）
            ssl_context = None
            if self.config.ssl_verify:
                ssl_context = True
            else:
                ssl_context = False
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=data_bytes,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                    ssl=ssl_context
                ) as response:
                    result = await response.read()
                    
                    if self._message_callback:
                        await self._safe_callback(self._message_callback, result)
                        
                    return response.status < 400
                    
        except ImportError:
            raise ConnectionError("aiohttp library not installed. Run: pip install aiohttp")
        except Exception as e:
            logger.error(f"HTTP request failed: {e}")
            return False

    async def disconnect(self):
        """断开连接"""
        async with self._lock:
            if self._status in [ConnectionStatus.DISCONNECTED, ConnectionStatus.CLOSED]:
                return
                
            old_status = self._status
            self._status = ConnectionStatus.CLOSED
            
            # 取消接收任务
            if self._receive_task:
                self._receive_task.cancel()
                try:
                    await self._receive_task
                except asyncio.CancelledError:
                    pass
                    
            # 取消心跳任务
            if self._ping_task:
                self._ping_task.cancel()
                try:
                    await self._ping_task
                except asyncio.CancelledError:
                    pass
            
            # 关闭连接
            try:
                if self.config.connection_type == ConnectionType.TCP:
                    if isinstance(self._connection, TCPConnection):
                        self._connection.writer.close()
                        try:
                            await self._connection.writer.wait_closed()
                        except:
                            pass
                elif self.config.connection_type == ConnectionType.UDP:
                    if self._connection and hasattr(self._connection, 'close'):
                        self._connection.close()
                elif self.config.connection_type == ConnectionType.WEBSOCKET:
                    if self._connection:
                        await self._connection.close()
                        
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
                
            self._connection = None
            self._receive_task = None
            self._ping_task = None
            
            logger.info(f"Disconnected from {self.config.host}:{self.config.port}")
            
            if old_status != ConnectionStatus.ERROR:
                await self._trigger_status_change()

    async def is_healthy(self) -> bool:
        """检查连接是否健康"""
        if self._status != ConnectionStatus.CONNECTED:
            return False
        
        try:
            # 根据不同的连接类型进行健康检查
            if self.config.connection_type == ConnectionType.TCP:
                # TCP 检查连接是否存在且可写
                if isinstance(self._connection, TCPConnection):
                    # 尝试写入空数据以检查连接状态
                    self._connection.writer.write(b'')
                    await asyncio.wait_for(self._connection.writer.drain(), timeout=1.0)
                    return True
            elif self.config.connection_type == ConnectionType.WEBSOCKET:
                # WebSocket 有内置的 ping 功能
                if self._connection and hasattr(self._connection, 'ping'):
                    await asyncio.wait_for(self._connection.ping(), timeout=1.0)
                    return True
            elif self.config.connection_type in [ConnectionType.HTTP, ConnectionType.HTTPS]:
                # 对于HTTP/HTTPS，可以尝试发送一个简单的GET请求
                import aiohttp
                protocol = "https" if self.config.connection_type == ConnectionType.HTTPS else "http"
                url = f"{protocol}://{self.config.host}:{self.config.port}{self.config.path or '/health'}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers=self.config.headers,
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                        ssl=False if not self.config.ssl_verify else True
                    ) as response:
                        return response.status < 400
            elif self.config.connection_type == ConnectionType.UDP:
                # UDP是无连接的协议，我们只能假设它是健康的（如果连接对象存在）
                return self._connection is not None
            
            return True
        except Exception:
            return False

    def _start_keepalive(self):
        """启动心跳保活"""
        async def keepalive_loop():
            while self._status == ConnectionStatus.CONNECTED:
                try:
                    await asyncio.sleep(30)  # 30秒心跳
                    if self._status == ConnectionStatus.CONNECTED:
                        await self.send(b'{"type":"ping"}')
                except Exception as e:
                    logger.debug(f"Keepalive error: {e}")
                    
        self._ping_task = asyncio.create_task(keepalive_loop())

    def set_message_callback(self, callback: MessageCallback):
        """设置消息接收回调"""
        self._message_callback = callback

    def set_error_callback(self, callback: ErrorCallback):
        """设置错误回调"""
        self._error_callback = callback

    def set_status_callback(self, callback: StatusCallback):
        """设置状态变更回调"""
        self._status_callback = callback

    async def _safe_callback(self, callback: Callable, *args, **kwargs):
        """安全执行回调"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Callback error: {e}")

    async def _trigger_status_change(self):
        """触发状态变更事件"""
        if self._status_callback:
            await self._safe_callback(self._status_callback, self._status)

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()


class ConnectionPool:
    """连接池 - 管理多个设备连接"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._connections: Dict[str, DeviceConnection] = {}
        self._lock = asyncio.Lock()
    
    async def get_connection(self, device_id: str, config: ConnectionConfig) -> DeviceConnection:
        """获取或创建连接"""
        async with self._lock:
            if device_id in self._connections:
                conn = self._connections[device_id]
                if await conn.is_healthy():
                    return conn
                else:
                    await conn.disconnect()
                    del self._connections[device_id]
            
            # 检查连接数限制
            if len(self._connections) >= self.max_connections:
                # 移除最旧的连接
                oldest_id = next(iter(self._connections))
                await self._connections[oldest_id].disconnect()
                del self._connections[oldest_id]
            
            conn = DeviceConnection(config)
            await conn.connect()
            self._connections[device_id] = conn
            return conn
    
    async def remove_connection(self, device_id: str):
        """移除指定连接"""
        async with self._lock:
            if device_id in self._connections:
                await self._connections[device_id].disconnect()
                del self._connections[device_id]
    
    async def close_all(self):
        """关闭所有连接"""
        async with self._lock:
            for conn in self._connections.values():
                await conn.disconnect()
            self._connections.clear()
    
    def get_connection_count(self) -> int:
        """获取当前连接数量"""
        return len(self._connections)
    
    def is_full(self) -> bool:
        """检查连接池是否已满"""
        return len(self._connections) >= self.max_connections
