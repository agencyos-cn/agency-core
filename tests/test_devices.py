#!/usr/bin/env python3
"""测试设备抽象层"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.devices import (
    SmartLightDevice, DeviceRegistry, DeviceDiscovery, 
    DiscoveryConfig, DiscoveryProtocol, CapabilityType
)

async def test_smart_light():
    print("\n🧪 测试智能灯泡设备")
    # 创建设备
    light = SmartLightDevice("light_001", "客厅灯")
    print(f"   ✅ 设备创建成功: {light.info.name}")
    # 连接
    await light.connect()
    print(f"   ✅ 设备连接成功")
    # 执行开关能力
    result = await light.execute(CapabilityType.SWITCH, state=True)
    print(f"   ✅ 开灯结果: {result['message']}")
    # 执行调光能力
    result = await light.execute(CapabilityType.DIMMER, brightness=75)
    print(f"   ✅ 调光结果: {result['message']}")
    # 获取状态
    state = await light.get_state()
    print(f"   ✅ 当前状态: {state}")
    # 断开连接
    await light.disconnect()
    print(f"   ✅ 设备断开")
    return light

async def test_device_registry():
    print("\n🧪 测试设备注册表")
    registry = DeviceRegistry()
    # 注册设备
    light1 = SmartLightDevice("light_001", "客厅灯")
    light2 = SmartLightDevice("light_002", "卧室灯")
    registry.register_device(light1)
    registry.register_device(light2)
    print(f"   ✅ 注册了 {len(registry.list_devices())} 个设备")
    # 按能力查找
    switch_devices = registry.find_devices_by_capability(CapabilityType.SWITCH)
    print(f"   ✅ 找到 {len(switch_devices)} 个支持开关的设备")
    return registry

async def main():
    print("=" * 50)
    print("🚀 设备抽象层测试开始")
    print("=" * 50)
    try:
        await test_smart_light()
        await test_device_registry()
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())