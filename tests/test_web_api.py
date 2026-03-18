"""Web API测试"""

import pytest
import asyncio
from aiohttp.test_utils import make_mocked_request
from aiohttp.web_exceptions import HTTPException
from unittest.mock import AsyncMock, MagicMock
import json

from src.core.runtime import AgentRuntime
from src.web.api import WebAPI, setup_app
from src.core.character import CharacterRoleType


@pytest.fixture
async def runtime():
    """创建运行时实例"""
    runtime = AgentRuntime()
    await runtime.initialize()
    yield runtime
    await runtime.shutdown()


@pytest.fixture
def api_instance(runtime):
    """创建API实例"""
    return WebAPI(runtime)


class TestWebAPIRoutes:
    """Web API路由测试"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, api_instance):
        """测试健康检查接口"""
        # 创建模拟请求
        from aiohttp.test_utils import make_mocked_request
        request = make_mocked_request('GET', '/api/health')
        
        # 调用处理函数
        response = await api_instance.health_check(request)
        
        # 检查响应
        assert response.status == 200
        data = json.loads(response.body)
        assert data["status"] == "healthy"
        assert data["service"] == "AgencyOS Core API"
    
    @pytest.mark.asyncio
    async def test_list_characters(self, api_instance, runtime):
        """测试列出角色接口"""
        user_id = "test_user_api"
        
        # 创建一个角色
        runtime.create_character(
            user_id=user_id,
            name="API测试角色",
            role_type="teacher",
            description="API测试用角色"
        )
        
        # 创建模拟请求
        from aiohttp.test_utils import make_mocked_request
        request = make_mocked_request('GET', f'/api/user/{user_id}/characters')
        # 手动添加匹配信息
        request.match_info = {'user_id': user_id}
        
        # 调用处理函数
        response = await api_instance.list_characters(request)
        
        # 检查响应
        assert response.status == 200
        data = json.loads(response.body)
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "API测试角色"
    
    @pytest.mark.asyncio
    async def test_get_character_detail(self, api_instance, runtime):
        """测试获取角色详情接口"""
        user_id = "test_user_detail"
        
        # 创建一个角色
        character = runtime.create_character(
            user_id=user_id,
            name="详情测试角色",
            role_type="assistant",
            description="详情测试用角色"
        )
        
        # 创建模拟请求
        from aiohttp.test_utils import make_mocked_request
        request = make_mocked_request('GET', f'/api/character/{character.id}')
        request.match_info = {'character_id': character.id}
        
        # 调用处理函数
        response = await api_instance.get_character_detail(request)
        
        # 检查响应
        assert response.status == 200
        data = json.loads(response.body)
        assert data["success"] is True
        assert data["data"]["name"] == "详情测试角色"
    
    @pytest.mark.asyncio
    async def test_create_character_api(self, api_instance):
        """测试创建角色API接口"""
        user_id = "test_user_create"
        
        # 模拟请求数据
        request_data = {
            "name": "新建角色",
            "role_type": "teacher",
            "description": "通过API创建的角色",
            "expertise_areas": ["教育", "培训"],
            "personality_traits": ["耐心", "专业"]
        }
        
        # 创建模拟请求
        from aiohttp.test_utils import make_mocked_request
        request = make_mocked_request('POST', f'/api/user/{user_id}/characters')
        request.match_info = {'user_id': user_id}
        
        # 模拟request.json()方法
        async def mock_json():
            return request_data
        
        request.json = mock_json
        
        # 调用处理函数
        response = await api_instance.create_character(request)
        
        # 检查响应
        assert response.status == 200
        data = json.loads(response.body)
        assert data["success"] is True
        assert data["data"]["name"] == "新建角色"
    
    @pytest.mark.asyncio
    async def test_update_character_api(self, api_instance, runtime):
        """测试更新角色API接口"""
        user_id = "test_user_update"
        
        # 创建一个角色
        character = runtime.create_character(
            user_id=user_id,
            name="待更新角色",
            role_type="assistant",
            description="更新前的描述"
        )
        
        # 模拟请求数据
        request_data = {
            "name": "已更新角色",
            "description": "更新后的描述"
        }
        
        # 创建模拟请求
        from aiohttp.test_utils import make_mocked_request
        request = make_mocked_request('PUT', f'/api/character/{character.id}')
        request.match_info = {'character_id': character.id}
        
        # 模拟request.json()方法
        async def mock_json():
            return request_data
        
        request.json = mock_json
        
        # 调用处理函数
        response = await api_instance.update_character(request)
        
        # 检查响应
        assert response.status == 200
        data = json.loads(response.body)
        assert data["success"] is True
        assert data["data"]["name"] == "已更新角色"
        assert data["data"]["description"] == "更新后的描述"
    
    @pytest.mark.asyncio
    async def test_get_available_roles(self, api_instance):
        """测试获取可用角色类型接口"""
        from aiohttp.test_utils import make_mocked_request
        request = make_mocked_request('GET', '/api/character/types')
        
        # 调用处理函数
        response = await api_instance.get_available_roles(request)
        
        # 检查响应
        assert response.status == 200
        data = json.loads(response.body)
        assert data["success"] is True
        assert len(data["data"]) > 0  # 应该有多个角色类型
        # 检查是否存在预期的角色类型
        role_values = [item["value"] for item in data["data"]]
        assert "teacher" in role_values
        assert "lawyer" in role_values
        assert "financial_advisor" in role_values


class TestWebApplication:
    """Web应用程序测试"""
    
    @pytest.mark.asyncio
    async def test_setup_app(self, runtime):
        """测试应用设置"""
        app = setup_app(runtime)
        
        # 检查应用是否正确设置了路由
        assert len(app.router.resources()) > 0  # 应该有多个路由
        
        # 验证健康检查路由存在
        resource = None
        for r in app.router.resources():
            if '/api/health' in r.canonical or r.canonical == '/api/health':
                resource = r
                break
        assert resource is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])