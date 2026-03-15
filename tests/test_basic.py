#!/usr/bin/env python3
"""AgencyOS 基础功能测试"""
"""
在根目录下，执行测试命令：
python tests/test_basic.py
"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.runtime import AgentRuntime, RuntimeContext


async def test_runtime_initialization():
    """测试运行时初始化"""
    print("\n🧪 测试 1: 运行时初始化")
    
    # 创建运行时实例
    runtime = AgentRuntime()
    print("   ✅ AgentRuntime 实例创建成功")
    
    # 初始化
    await runtime.initialize()
    print("   ✅ AgentRuntime 初始化成功")
    
    return runtime


async def test_process_input(runtime):
    """测试处理用户输入"""
    print("\n🧪 测试 2: 处理用户输入")
    
    # 创建上下文
    context = RuntimeContext(
        user_id="test_user_001",
        session_id="test_session_001"
    )
    print(f"   ✅ 上下文创建成功: user={context.user_id}, session={context.session_id}")
    
    # 测试各种输入
    test_inputs = [
        "开灯",
        "今天天气怎么样",
        "你好"
    ]
    
    for i, user_input in enumerate(test_inputs):
        print(f"\n   📝 输入 {i+1}: \"{user_input}\"")
        
        # 处理输入
        result = await runtime.process(user_input, context)
        
        # 输出结果
        print(f"   📦 意图: {runtime.intent_engine._rule_based_parse(user_input)}")
        print(f"   💬 回答: {result.get('answer', '无回答')}")
        
        if result.get('results'):
            print(f"   🔧 执行了 {len(result['results'])} 个技能")
    
    print("\n   ✅ 所有输入处理完成")


async def test_shutdown(runtime):
    """测试运行时关闭"""
    print("\n🧪 测试 3: 运行时关闭")
    
    await runtime.shutdown()
    print("   ✅ AgentRuntime 关闭成功")


async def main():
    """主测试函数"""
    print("=" * 50)
    print("🚀 AgencyOS 基础功能测试开始")
    print("=" * 50)
    
    try:
        # 测试 1: 初始化
        runtime = await test_runtime_initialization()
        
        # 测试 2: 处理输入
        await test_process_input(runtime)
        
        # 测试 3: 关闭
        await test_shutdown(runtime)
        
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)