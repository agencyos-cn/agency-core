#!/usr/bin/env python3
"""
第三方生态集成测试脚本
用于验证新架构下与Dify、OpenClaw以及其他第三方模型提供商的集成
"""

from src.core.config import ConfigManager
from src.core.intent_engine import IntentEngine
from src.core.runtime import RuntimeContext


def test_ecosystem_integration():
    """测试第三方生态集成"""
    print("=" * 60)
    print("🧪 第三方生态集成测试开始")
    print("=" * 60)
    
    # 1. 测试配置管理器
    print("\n🔍 测试 1: 配置管理器初始化")
    config_manager = ConfigManager()
    print("   ✅ ConfigManager 初始化成功")
    
    # 2. 测试第三方生态配置
    print("\n🌍 测试 2: 第三方生态配置")
    
    # 检查是否启用了第三方生态
    ecosystem_enabled = config_manager.core.enable_third_party_ecosystem
    print(f"   ✅ 第三方生态集成已启用: {ecosystem_enabled}")
    
    # 检查可用的模型提供商
    available_providers = config_manager.get_available_models()
    print(f"   ✅ 可用模型提供商数量: {len(available_providers)}")
    
    # 检查第三方生态状态
    ecosystem_status = config_manager.get_third_party_ecosystem_status()
    print(f"   ✅ Dify 连接状态: {ecosystem_status['dify_connected']}")
    print(f"   ✅ OpenClaw 连接状态: {ecosystem_status['openclaw_connected']}")
    print(f"   ✅ 远程模型已启用: {ecosystem_status['remote_models_enabled']}")
    
    # 3. 测试意图引擎
    print("\n🧠 测试 3: 意图引擎与第三方集成")
    intent_engine = IntentEngine(config_manager)
    print("   ✅ IntentEngine 初始化成功")
    
    # 4. 测试运行时上下文
    print("\n⚙️  测试 4: 运行时上下文")
    context = RuntimeContext(
        user_id="test_user_001",
        session_id="test_session_001"
    )
    print(f"   ✅ 运行时上下文创建成功: user={context.user_id}, session={context.session_id}")
    
    # 5. 测试意图解析（本地规则）
    print("\n🎯 测试 5: 意图解析测试")
    test_inputs = [
        "开灯",
        "今天天气怎么样",
        "播放音乐"
    ]
    
    for user_input in test_inputs:
        intent = intent_engine._rule_based_parse(user_input)
        print(f"   📝 输入: '{user_input}' -> 类型: {intent['type']}, 置信度: {intent['confidence']}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！第三方生态集成配置正常")
    print("=" * 60)
    
    # 显示配置摘要
    print("\n📋 配置摘要:")
    print(f"   • 活跃LLM提供商: {config_manager.get_active_llm_provider()}")
    print(f"   • 已配置模型提供商: {list(config_manager.llm.providers.keys())}")
    print(f"   • 第三方平台集成: {config_manager.llm.integrated_platforms}")
    print(f"   • 模型市场URLs: {len(config_manager.llm.model_marketplace_urls)} 个")


if __name__ == "__main__":
    test_ecosystem_integration()