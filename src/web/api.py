"""Web API接口 - 为前端提供REST API"""

import json
import logging
from typing import Dict, Any, Optional
from aiohttp import web, hdrs
import asyncio

from src.core.runtime import AgentRuntime
from src.core.character import CharacterAPI
from src.core.config import ConfigManager

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


class WebAPI:
    """Web API类，提供REST接口给前端使用"""
    
    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime
        self.character_api = CharacterAPI(self.runtime.character_manager)
        self.config_manager = ConfigManager()
    
    @routes.get('/api/health')
    async def health_check(self, request: web.Request) -> web.Response:
        """健康检查接口"""
        return web.json_response({
            "status": "healthy",
            "service": "AgencyOS Core API"
        })
    
    @routes.get('/api/user/{user_id}/characters')
    async def list_characters(self, request: web.Request) -> web.Response:
        """获取用户的所有角色"""
        user_id = request.match_info['user_id']
        result = self.character_api.list_characters(user_id)
        return web.json_response(result)
    
    @routes.get('/api/character/{character_id}')
    async def get_character_detail(self, request: web.Request) -> web.Response:
        """获取角色详情"""
        character_id = request.match_info['character_id']
        result = self.character_api.get_character_detail(character_id)
        return web.json_response(result)
    
    @routes.post('/api/user/{user_id}/characters')
    async def create_character(self, request: web.Request) -> web.Response:
        """创建新角色"""
        user_id = request.match_info['user_id']
        try:
            data = await request.json()
            result = self.character_api.create_character_api(user_id, data)
            return web.json_response(result)
        except json.JSONDecodeError:
            return web.json_response({
                "success": False,
                "error": "无效的JSON数据"
            }, status=400)
    
    @routes.put('/api/character/{character_id}')
    async def update_character(self, request: web.Request) -> web.Response:
        """更新角色"""
        character_id = request.match_info['character_id']
        try:
            data = await request.json()
            result = self.character_api.update_character_api(character_id, data)
            return web.json_response(result)
        except json.JSONDecodeError:
            return web.json_response({
                "success": False,
                "error": "无效的JSON数据"
            }, status=400)
    
    @routes.delete('/api/user/{user_id}/characters/{character_id}')
    async def delete_character(self, request: web.Request) -> web.Response:
        """删除角色"""
        user_id = request.match_info['user_id']
        character_id = request.match_info['character_id']
        result = self.character_api.delete_character_api(user_id, character_id)
        return web.json_response(result)
    
    @routes.post('/api/user/{user_id}/characters/{character_id}/switch')
    async def switch_character(self, request: web.Request) -> web.Response:
        """切换角色"""
        user_id = request.match_info['user_id']
        character_id = request.match_info['character_id']
        result = self.character_api.switch_character_api(user_id, character_id)
        return web.json_response(result)
    
    @routes.get('/api/character/types')
    async def get_available_roles(self, request: web.Request) -> web.Response:
        """获取可用的角色类型"""
        result = self.character_api.get_available_roles()
        return web.json_response(result)
    
    @routes.get('/api/config')
    async def get_config(self, request: web.Request) -> web.Response:
        """获取系统配置"""
        return web.json_response({
            "success": True,
            "data": {
                "has_llm_config": self.config_manager.has_llm_config(),
                "has_dify_config": self.config_manager.has_dify_config(),
                "has_openclaw_config": self.config_manager.has_openclaw_config(),
                "llm_providers": list(self.config_manager.llm.providers.keys()) if self.config_manager.llm.providers else [],
                "integrated_platforms": self.config_manager.llm.integrated_platforms or []
            }
        })
    
    @routes.post('/api/chat/process')
    async def process_chat(self, request: web.Request) -> web.Response:
        """处理聊天请求"""
        try:
            data = await request.json()
            user_input = data.get('message', '')
            user_id = data.get('user_id', '')
            character_id = data.get('character_id', None)
            
            if not user_input or not user_id:
                return web.json_response({
                    "success": False,
                    "error": "缺少必要参数"
                }, status=400)
            
            # 创建运行时上下文
            from src.core.runtime import RuntimeContext
            context = RuntimeContext(
                user_id=user_id,
                session_id=f"session_{int(asyncio.time.time())}",
                character_id=character_id
            )
            
            # 处理用户输入
            result = await self.runtime.process(user_input, context)
            
            return web.json_response({
                "success": True,
                "data": result
            })
        except Exception as e:
            logger.error(f"处理聊天请求时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)


def setup_app(runtime: AgentRuntime) -> web.Application:
    """设置Web应用程序"""
    app = web.Application()
    api = WebAPI(runtime)
    
    # 添加路由
    app.add_routes(routes)
    
    # 添加CORS中间件
    async def cors_middleware(app, handler):
        async def middleware(request):
            # 允许跨域请求
            response = await handler(request)
            response.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = "*"
            response.headers[hdrs.ACCESS_CONTROL_ALLOW_HEADERS] = "*"
            response.headers[hdrs.ACCESS_CONTROL_ALLOW_METHODS] = "*"
            return response
        return middleware
    
    app.middlewares.append(cors_middleware)
    
    return app