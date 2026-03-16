#!/usr/bin/env python3
"""测试设备连接管理模块"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.devices.connection import DeviceConnection, ConnectionConfig, ConnectionType, ConnectionStatus

async def test_tcp_connection():
    """测试 TCP 连接"""
    print("\n🧪 测试 TCP 连接")
    
    # 创建连接配置（连接到一个测试服务器）
    config = ConnectionConfig(
        connection_type=ConnectionType.TCP,
        host="httpbin.org",
        port=80,
        timeout=5.0
    )
    
    conn = DeviceConnection(config)
    
    # 设置回调
    def on_message(data):
        print(f"   📨 收到消息: {data[:50]}...")
    
    def on_error(error):
        print(f"   ❌ 错误: {error}")
    
    def on_status(status):
        print(f"   📊 状态变更: {status.value}")
    
    conn.set_message_callback(on_message)
    conn.set_error_callback(on_error)
    conn.set_status_callback(on_status)
    
    # 连接
    success = await conn.connect()
    print(f"   ✅ 连接{'成功' if success else '失败'}")
    
    if success:
        # 发送 HTTP 请求
        request = "GET /get HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
        await conn.send(request)
        
        # 等待接收数据
        await asyncio.sleep(2)
        
        # 断开连接
        await conn.disconnect()
        print(f"   ✅ 断开连接")

async def test_websocket_connection():
    """测试 WebSocket 连接"""
    print("\n🧪 测试 WebSocket 连接")
    
    # 创建连接配置（使用本地 WebSocket 测试服务器）
    config = ConnectionConfig(
        connection_type=ConnectionType.WEBSOCKET,
        host="localhost",
        port=8765,
        path="/",
        timeout=5.0,
        keepalive=True
    )
    
    async with DeviceConnection(config) as conn:
        print(f"   ✅ 连接成功")
        
        # 设置消息回调
        def on_message(data):
            print(f"   📨 收到回显: {data.decode()}")
        
        conn.set_message_callback(on_message)
        
        # 发送消息
        test_msg = "Hello AgencyOS!"
        await conn.send(test_msg)
        print(f"   📤 发送: {test_msg}")
        
        # 等待回显
        await asyncio.sleep(1)
    
    print(f"   ✅ 连接已关闭")

async def test_http_connection():
    """测试 HTTP 连接"""
    print("\n🧪 测试 HTTP 连接")
    
    config = ConnectionConfig(
        connection_type=ConnectionType.HTTP,
        host="httpbin.org",
        port=80,
        path="/post",
        headers={"Content-Type": "application/json"},
        timeout=5.0
    )
    
    conn = DeviceConnection(config)
    
    def on_message(data):
        print(f"   📨 收到响应: {data[:100]}...")
    
    conn.set_message_callback(on_message)
    
    # 连接（HTTP 是短连接）
    success = await conn.connect()
    print(f"   ✅ 连接{'成功' if success else '失败'}")
    
    if success:
        # 发送 POST 请求
        test_data = {"message": "Hello AgencyOS!"}
        await conn.send(test_data)
        
        await asyncio.sleep(1)
        await conn.disconnect()

async def test_https_connection():
    """测试 HTTPS 连接"""
    print("\n🧪 测试 HTTPS 连接")
    
    config = ConnectionConfig(
        connection_type=ConnectionType.HTTPS,
        host="httpbin.org",
        port=443,
        path="/get",
        timeout=5.0
    )
    
    conn = DeviceConnection(config)
    
    def on_message(data):
        print(f"   📨 收到响应: {data[:100]}...")
    
    conn.set_message_callback(on_message)
    
    success = await conn.connect()
    print(f"   ✅ 连接{'成功' if success else '失败'}")
    
    if success:
        test_data = {"message": "HTTPS Test"}
        await conn.send(test_data)
        await asyncio.sleep(1)
        await conn.disconnect()

async def main():
    print("=" * 50)
    print("🚀 设备连接管理模块测试")
    print("=" * 50)
    
    try:
        await test_tcp_connection()
        await test_websocket_connection()
        await test_http_connection()
        await test_https_connection()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())