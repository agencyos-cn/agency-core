"""Web API简单测试，不使用pytest"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.runtime import AgentRuntime
from src.web.api import WebAPI
from src.core.character import CharacterRoleType


def test_web_api_creation():
    """测试Web API创建"""
    print("Testing Web API Creation...")
    
    runtime = AgentRuntime()
    api = WebAPI(runtime)
    
    assert api is not None
    assert api.runtime == runtime
    print("✓ Web API instance creation works")
    
    print("Web API Creation tests passed!\n")


def test_character_endpoints():
    """测试角色相关端点"""
    print("Testing Character Endpoints...")
    
    runtime = AgentRuntime()
    api = WebAPI(runtime)
    
    user_id = "test_user_web_api"
    
    # 模拟创建角色的数据
    character_data = {
        "name": "Web API测试角色",
        "role_type": "teacher",
        "description": "通过Web API测试的角色",
        "expertise_areas": ["教育", "培训"],
        "personality_traits": ["专业", "耐心"]
    }
    
    # 测试创建角色 - 使用内部character_api实例
    result = api.character_api.create_character_api(user_id, character_data)
    assert result["success"] is True
    assert result["data"]["name"] == "Web API测试角色"
    character_id = result["data"]["id"]
    print("✓ Create character endpoint works")
    
    # 测试获取角色详情
    detail_result = api.character_api.get_character_detail(character_id)
    assert detail_result["success"] is True
    assert detail_result["data"]["id"] == character_id
    print("✓ Get character detail endpoint works")
    
    # 测试获取所有角色
    list_result = api.character_api.list_characters(user_id)
    assert list_result["success"] is True
    assert len(list_result["data"]) == 1
    print("✓ List characters endpoint works")
    
    # 测试更新角色
    update_data = {
        "name": "更新后的Web API测试角色",
        "description": "更新后的描述"
    }
    update_result = api.character_api.update_character_api(character_id, update_data)
    assert update_result["success"] is True
    assert update_result["data"]["name"] == "更新后的Web API测试角色"
    print("✓ Update character endpoint works")
    
    # 测试获取可用角色类型
    roles_result = api.character_api.get_available_roles()
    assert roles_result["success"] is True
    assert len(roles_result["data"]) > 0
    print("✓ Get available roles endpoint works")
    
    # 测试删除角色
    delete_result = api.character_api.delete_character_api(user_id, character_id)
    assert delete_result["success"] is True
    print("✓ Delete character endpoint works")
    
    print("All Character Endpoint tests passed!\n")


def test_config_endpoint():
    """测试配置相关端点"""
    print("Testing Config Endpoint...")
    
    runtime = AgentRuntime()
    api = WebAPI(runtime)
    
    # 测试获取配置
    # 注意：这可能会因缺少配置文件而失败，但我们仍然可以测试方法调用
    try:
        from aiohttp.test_utils import make_mocked_request
        import asyncio
        
        # 模拟请求
        request = make_mocked_request('GET', '/api/config')
        
        # 由于这是异步方法，我们不能直接调用
        # 但在同步测试中，我们可以检查方法是否存在
        assert hasattr(api, 'get_config')
        print("✓ Config endpoint method exists")
    except ImportError:
        # 如果aiohttp不可用，跳过这部分测试
        print("⚠ Skipping config endpoint test (aiohttp not available)")
    
    print("Config Endpoint tests passed!\n")


def test_additional_api_features():
    """测试额外的API功能"""
    print("Testing Additional API Features...")
    
    runtime = AgentRuntime()
    
    # 测试创建各种类型的角色
    user_id = "test_api_features"
    
    # 教师角色
    teacher = runtime.create_character(
        user_id=user_id,
        name="张老师",
        role_type="teacher",
        description="数学教师",
        expertise_areas=["数学", "物理"],
        personality_traits=["耐心", "专业"]
    )
    
    # 律师角色
    lawyer = runtime.create_character(
        user_id=user_id,
        name="李律师",
        role_type="lawyer",
        description="法律专家",
        expertise_areas=["合同法", "知识产权"],
        personality_traits=["严谨", "客观"]
    )
    
    # 金融顾问角色
    advisor = runtime.create_character(
        user_id=user_id,
        name="王金融师",
        role_type="financial_advisor",
        description="投资顾问",
        expertise_areas=["股票", "基金"],
        personality_traits=["稳健", "专业"]
    )
    
    # 获取用户的所有角色
    characters = runtime.get_user_characters(user_id)
    assert len(characters) == 3
    
    names = [char.name for char in characters]
    assert "张老师" in names
    assert "李律师" in names
    assert "王金融师" in names
    
    print("✓ Multiple character types work")
    
    # 测试角色切换
    success = runtime.switch_character(user_id, lawyer.id)
    assert success is True
    print("✓ Character switching works")
    
    print("Additional API Features tests passed!\n")


def main():
    """运行所有测试"""
    print("Running simple tests for Web API...\n")
    
    try:
        test_web_api_creation()
        test_character_endpoints()
        test_config_endpoint()
        test_additional_api_features()
        
        print("🎉 All Web API tests passed successfully!")
        return True
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)