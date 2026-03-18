"""Web API接口 - 为前端提供REST API"""

import json
import logging
import time
from typing import Dict, Any, Optional
from aiohttp import web, hdrs
import asyncio

from src.core.runtime import AgentRuntime
from src.core.character import CharacterAPI
from src.core.config import ConfigManager
# 导入新增的认证模块
from src.core.auth.user_manager import UserManager
import jwt
from datetime import timedelta

logger = logging.getLogger(__name__)


class WebAPI:
    """Web API类，提供REST接口给前端使用"""
    
    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime
        self.character_api = CharacterAPI(self.runtime.character_manager)
        self.config_manager = ConfigManager()
        
    async def health_check(self, request: web.Request) -> web.Response:
        """健康检查接口"""
        return web.json_response({
            "status": "healthy",
            "service": "AgencyOS Core API"
        })
    
    async def list_characters(self, request: web.Request) -> web.Response:
        """获取用户的所有角色"""
        user_id = request.match_info['user_id']
        result = self.character_api.list_characters(user_id)
        return web.json_response(result)
    
    async def get_character_detail(self, request: web.Request) -> web.Response:
        """获取角色详情"""
        character_id = request.match_info['character_id']
        result = self.character_api.get_character_detail(character_id)
        return web.json_response(result)
    
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
    
    async def delete_character(self, request: web.Request) -> web.Response:
        """删除角色"""
        user_id = request.match_info['user_id']
        character_id = request.match_info['character_id']
        result = self.character_api.delete_character_api(user_id, character_id)
        return web.json_response(result)
    
    async def switch_character(self, request: web.Request) -> web.Response:
        """切换角色"""
        user_id = request.match_info['user_id']
        character_id = request.match_info['character_id']
        result = self.character_api.switch_character_api(user_id, character_id)
        return web.json_response(result)
    
    async def get_available_roles(self, request: web.Request) -> web.Response:
        """获取可用的角色类型"""
        result = self.character_api.get_available_roles()
        return web.json_response(result)
    
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
                session_id=f"session_{int(time.time())}",
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
    
    # 认证相关方法
    async def register(self, request: web.Request) -> web.Response:
        """用户注册"""
        try:
            data = await request.json()
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            
            if not name or not email or not password:
                return web.json_response({
                    "success": False,
                    "error": "姓名、邮箱和密码都是必填项"
                }, status=400)
            
            user_manager = UserManager()
            user = user_manager.create_user(name, email, password)
            
            if user:
                return web.json_response({
                    "success": True,
                    "message": "用户注册成功"
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "邮箱已被注册"
                }, status=400)
        except Exception as e:
            logger.error(f"注册用户时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "注册失败"
            }, status=500)

    async def login(self, request: web.Request) -> web.Response:
        """用户登录"""
        try:
            data = await request.json()
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return web.json_response({
                    "success": False,
                    "error": "邮箱和密码都是必填项"
                }, status=400)
            
            user_manager = UserManager()
            user = user_manager.authenticate_user(email, password)
            
            if not user:
                return web.json_response({
                    "success": False,
                    "error": "邮箱或密码错误"
                }, status=401)
            
            # 创建访问令牌
            access_token_expires = timedelta(minutes=30)  # 30分钟过期
            token_data = {
                "sub": user.email,
                "user_id": user.id,
                "user_role": user.role
            }
            access_token = user_manager.create_access_token(
                data=token_data, expires_delta=access_token_expires
            )
            
            return web.json_response({
                "success": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                },
                "token": access_token,
                "token_type": "bearer"
            })
        except Exception as e:
            logger.error(f"登录用户时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "登录失败"
            }, status=500)

    async def get_current_user(self, request: web.Request) -> web.Response:
        """获取当前用户信息"""
        try:
            # 这里需要实现JWT令牌验证逻辑
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return web.json_response({
                    "success": False,
                    "error": "未提供认证令牌"
                }, status=401)
            
            token = auth_header.split(' ')[1]
            
            try:
                # 解码JWT令牌
                user_manager = UserManager()
                payload = jwt.decode(token, user_manager.secret_key, algorithms=["HS256"])
                email: str = payload.get("sub")
                if email is None:
                    return web.json_response({
                        "success": False,
                        "error": "无效的令牌"
                    }, status=401)
            except jwt.PyJWTError:
                return web.json_response({
                    "success": False,
                    "error": "无效的令牌"
                }, status=401)
            
            user = user_manager.get_user_by_email(email)
            
            if user is None:
                return web.json_response({
                    "success": False,
                    "error": "用户不存在"
                }, status=401)
            
            return web.json_response({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            })
        except Exception as e:
            logger.error(f"获取当前用户时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "获取用户信息失败"
            }, status=500)


def setup_app(runtime: AgentRuntime) -> web.Application:
    """设置Web应用程序"""
    app = web.Application()
    api_instance = WebAPI(runtime)
    
    # 添加路由
    app.router.add_get('/api/health', api_instance.health_check)
    app.router.add_get('/api/user/{user_id}/characters', api_instance.list_characters)
    app.router.add_get('/api/character/{character_id}', api_instance.get_character_detail)
    app.router.add_post('/api/user/{user_id}/characters', api_instance.create_character)
    app.router.add_put('/api/character/{character_id}', api_instance.update_character)
    app.router.add_delete('/api/user/{user_id}/characters/{character_id}', api_instance.delete_character)
    app.router.add_post('/api/user/{user_id}/characters/{character_id}/switch', api_instance.switch_character)
    app.router.add_get('/api/character/types', api_instance.get_available_roles)
    app.router.add_get('/api/config', api_instance.get_config)
    app.router.add_post('/api/chat/process', api_instance.process_chat)
    
    # 认证相关路由
    app.router.add_post('/api/auth/register', api_instance.register)
    app.router.add_post('/api/auth/login', api_instance.login)
    app.router.add_get('/api/auth/me', api_instance.get_current_user)
    
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