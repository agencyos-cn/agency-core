"""角色系统简单测试，不使用pytest"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.character import CharacterManager, CharacterRoleType, CharacterProfile
from src.core.runtime import AgentRuntime, RuntimeContext


def test_character_manager():
    """测试角色管理器"""
    print("Testing Character Manager...")
    
    manager = CharacterManager()
    user_id = "test_user_simple"
    
    # 测试创建角色
    character = manager.create_character(
        user_id=user_id,
        name="李老师",
        role_type=CharacterRoleType.TEACHER,
        description="资深教育专家",
        expertise_areas=["数学", "物理"],
        personality_traits=["耐心", "细致"]
    )
    
    assert character.name == "李老师"
    assert character.role_type == CharacterRoleType.TEACHER
    assert "数学" in character.expertise_areas
    print("✓ Character creation works")
    
    # 测试获取用户角色
    characters = manager.get_user_characters(user_id)
    assert len(characters) == 1
    assert characters[0].name == "李老师"
    print("✓ Get user characters works")
    
    # 测试更新角色
    success = manager.update_character(
        character_id=character.id,
        name="更新后的李老师",
        description="更新后的描述"
    )
    assert success is True
    updated_char = manager.get_character(character.id)
    assert updated_char.name == "更新后的李老师"
    print("✓ Update character works")
    
    # 测试角色序列化
    char_dict = character.to_dict()
    assert char_dict["name"] == "更新后的李老师"
    assert char_dict["role_type"] == "teacher"
    print("✓ Character to_dict works")
    
    # 测试删除角色
    success = manager.delete_character(user_id, character.id)
    assert success is True
    remaining = manager.get_user_characters(user_id)
    assert len(remaining) == 0
    print("✓ Delete character works")
    
    print("All Character Manager tests passed!\n")


def test_runtime_integration():
    """测试运行时集成"""
    print("Testing Runtime Integration...")
    
    runtime = AgentRuntime()
    
    # 注意：我们不会在这里初始化runtime，因为可能需要外部服务
    # 而是测试那些不需要外部依赖的部分
    
    user_id = "test_user_runtime"
    
    # 测试创建角色
    character = runtime.create_character(
        user_id=user_id,
        name="测试角色",
        role_type="teacher",
        description="集成测试角色",
        expertise_areas=["教育", "培训"],
        personality_traits=["友好", "专业"]
    )
    
    assert character.name == "测试角色"
    assert character.description == "集成测试角色"
    print("✓ Runtime character creation works")
    
    # 测试获取用户角色
    characters = runtime.get_user_characters(user_id)
    assert len(characters) == 1
    assert characters[0].name == "测试角色"
    print("✓ Runtime get user characters works")
    
    print("All Runtime Integration tests passed!\n")


def test_character_api():
    """测试角色API"""
    print("Testing Character API...")
    
    from src.core.character import CharacterAPI
    
    runtime = AgentRuntime()
    api = CharacterAPI(runtime.character_manager)
    
    user_id = "test_user_api"
    
    # 测试创建角色API
    character_data = {
        "name": "API测试角色",
        "role_type": "teacher",
        "description": "通过API创建的角色",
        "expertise_areas": ["教育", "培训"],
        "personality_traits": ["专业", "耐心"]
    }
    
    result = api.create_character_api(user_id, character_data)
    assert result["success"] is True
    assert result["data"]["name"] == "API测试角色"
    character_id = result["data"]["id"]
    print("✓ Create character API works")
    
    # 测试获取角色详情
    detail_result = api.get_character_detail(character_id)
    assert detail_result["success"] is True
    assert detail_result["data"]["id"] == character_id
    print("✓ Get character detail API works")
    
    # 测试更新角色
    update_data = {
        "name": "更新后的API测试角色",
        "description": "更新后的描述"
    }
    update_result = api.update_character_api(character_id, update_data)
    assert update_result["success"] is True
    assert update_result["data"]["name"] == "更新后的API测试角色"
    print("✓ Update character API works")
    
    # 测试获取可用角色类型
    roles_result = api.get_available_roles()
    assert roles_result["success"] is True
    assert len(roles_result["data"]) > 0
    print("✓ Get available roles API works")
    
    # 测试删除角色
    delete_result = api.delete_character_api(user_id, character_id)
    assert delete_result["success"] is True
    print("✓ Delete character API works")
    
    print("All Character API tests passed!\n")


def main():
    """运行所有测试"""
    print("Running simple tests for character system...\n")
    
    try:
        test_character_manager()
        test_runtime_integration()
        test_character_api()
        
        print("🎉 All tests passed successfully!")
        return True
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)