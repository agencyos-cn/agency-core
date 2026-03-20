"""Web API接口 - 为前端提供REST API"""

import json
import logging
import time
from typing import Dict, Any, Optional
from aiohttp import web, hdrs
import asyncio
import jwt
from datetime import datetime
from src.core.runtime import AgentRuntime
from src.core.character import CharacterAPI
from src.core.config import ConfigManager
from src.core.database.models import User  # 导入User模型
# 导入新增的认证模块
from src.core.auth.user_manager import UserManager
from src.core.auth.mail_service import MailService  # 导入邮件服务
from src.version import __version__


logger = logging.getLogger(__name__)


class WebAPI:
    """Web API类，提供REST接口给前端使用"""
    
    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime
        self.character_api = CharacterAPI(self.runtime.character_manager)
        self.config_manager = ConfigManager()
        self.user_manager = UserManager()
        
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
            # 前端发送的是name，所以应该获取name字段
            name = data.get('nickname')
            email = data.get('email')
            password = data.get('password')
            
            if not name or not email or not password:
                return web.json_response({
                    "success": False,
                    "error": "姓名、邮箱和密码都是必填项"
                }, status=400)
            
            # 使用WebAPI类中的user_manager实例
            user = self.user_manager.create_user(name, email, password)
            
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
            
            user = self.user_manager.authenticate_user(email, password)
            
            if not user:
                # 获取用户是否存在以提供更准确的错误消息
                existing_user = self.user_manager.get_user_by_email(email)
                if existing_user:
                    logger.warning(f"登录失败: 用户 {email} 密码错误")
                    return web.json_response({
                        "success": False,
                        "error": "密码错误"
                    }, status=401)
                else:
                    logger.info(f"登录失败: 用户 {email} 不存在")
                    return web.json_response({
                        "success": False,
                        "error": "用户不存在"
                    }, status=401)
            
            # 创建访问令牌
            access_token_expires = timedelta(minutes=30)  # 30分钟过期
            token_data = {
                "sub": user.email,
                "user_id": user.id,
                "user_role": user.status
            }
            # 使用配置中的密钥
            secret_key = self.config_manager.security.encryption_key
            access_token = jwt.encode(token_data, secret_key, algorithm="HS256")
            
            logger.info(f"用户 {email} 成功登录")
            return web.json_response({
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "avatar_url": user.avatar_url,
                    "status": user.status
                },
                "token": access_token,
                "token_type": "bearer"
            })
        except json.JSONDecodeError:
            logger.error("登录请求解析JSON失败")
            return web.json_response({
                "success": False,
                "error": "无效的JSON数据"
            }, status=400)
        except Exception as e:
            logger.error(f"登录用户时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "登录失败"
            }, status=500)

    async def request_password_reset(self, request: web.Request) -> web.Response:
        """请求密码重置 - 发送验证码到邮箱"""
        try:
            data = await request.json()
            email = data.get('email')
            
            if not email:
                return web.json_response({
                    "success": False,
                    "error": "邮箱是必填项"
                }, status=400)
            
            # 检查用户是否存在
            user = self.user_manager.get_user_by_email(email)
            
            if not user:
                logger.warning(f"尝试为不存在的用户 {email} 重置密码")
                # 为了安全，不透露用户是否存在
                return web.json_response({
                    "success": True,
                    "message": "如果邮箱存在，验证码将发送到该邮箱"
                })
            
            # 发送验证码
            mail_service = MailService()
            try:
                mail_service.send_verification_code(
                    recipient_email=email,
                    subject="密码重置验证码 - AgencyOS"
                )
                logger.info(f"密码重置验证码已发送到 {email}")
                
                return web.json_response({
                    "success": True,
                    "message": "验证码已发送到您的邮箱"
                })
            except Exception as e:
                logger.error(f"发送验证码失败: {str(e)}")
                return web.json_response({
                    "success": False,
                    "error": "发送验证码失败，请稍后再试"
                }, status=500)
                
        except Exception as e:
            logger.error(f"请求密码重置时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "请求失败"
            }, status=500)

    async def reset_password(self, request: web.Request) -> web.Response:
        """重置密码 - 使用邮箱和验证码"""
        try:
            data = await request.json()
            email = data.get('email')
            code = data.get('code')
            new_password = data.get('new_password')
            
            if not email or not code or not new_password:
                return web.json_response({
                    "success": False,
                    "error": "邮箱、验证码和新密码都是必填项"
                }, status=400)
            
            # 验证密码强度（至少6位）
            if len(new_password) < 6:
                return web.json_response({
                    "success": False,
                    "error": "新密码长度不能少于6位"
                }, status=400)
            
            # 验证验证码
            mail_service = MailService()
            if not mail_service.verify_code(email, code):
                logger.warning(f"密码重置失败: 验证码错误或已失效 - {email}")
                return web.json_response({
                    "success": False,
                    "error": "验证码错误或已失效"
                }, status=400)
            
            # 更新用户密码
            user = self.user_manager.get_user_by_email(email)
            
            if not user:
                logger.warning(f"密码重置失败: 用户不存在 - {email}")
                return web.json_response({
                    "success": False,
                    "error": "用户不存在"
                }, status=400)
            
            # 直接在数据库中更新密码
            connection = self.user_manager.get_connection()
            cursor = connection.cursor()
            
            password_hash = User.hash_password(new_password)
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE email = %s",
                (password_hash, email)
            )
            connection.commit()
            connection.close()
            
            logger.info(f"用户 {email} 的密码已重置")
            return web.json_response({
                "success": True,
                "message": "密码重置成功"
            })
            
        except Exception as e:
            logger.error(f"重置密码时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "密码重置失败"
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
                secret_key = self.config_manager.security.encryption_key
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
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
            
            user = self.user_manager.get_user_by_email(email)
            
            if user is None:
                return web.json_response({
                    "success": False,
                    "error": "用户不存在"
                }, status=401)
            
            return web.json_response({
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "status": user.status
            })
        except Exception as e:
            logger.error(f"获取当前用户时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "获取用户信息失败"
            }, status=500)
    
    async def get_user_agents(self, request: web.Request) -> web.Response:
        """获取用户的所有智能体实例"""
        try:
            # 从请求路径参数中获取用户ID
            user_id = int(request.match_info.get('user_id'))
            
            # 验证用户身份
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return web.json_response({
                    "success": False,
                    "error": "未提供认证令牌"
                }, status=401)
            
            token = auth_header.split(' ')[1]
            
            try:
                # 解码JWT令牌
                secret_key = self.config_manager.security.encryption_key
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                token_user_id = payload.get("user_id")
                
                # 确保请求的用户ID与令牌中的用户ID匹配
                if str(token_user_id) != str(user_id):
                    return web.json_response({
                        "success": False,
                        "error": "无权访问其他用户的智能体"
                    }, status=403)
            except jwt.PyJWTError:
                return web.json_response({
                    "success": False,
                    "error": "无效的令牌"
                }, status=401)
            
            # 获取用户智能体列表
            agents = self.user_manager.get_user_agents(user_id)
            
            return web.json_response({
                "success": True,
                "agents": agents
            })
        except Exception as e:
            logger.error(f"获取用户智能体时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "获取智能体列表失败"
            }, status=500)

    async def get_agent_detail(self, request: web.Request) -> web.Response:
        """获取特定智能体实例详情"""
        try:
            # 从请求路径参数获取用户ID和智能体ID
            user_id = int(request.match_info.get('user_id'))
            agent_id = int(request.match_info.get('agent_id'))
            
            # 验证用户身份
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return web.json_response({
                    "success": False,
                    "error": "未提供认证令牌"
                }, status=401)
            
            token = auth_header.split(' ')[1]
            
            try:
                # 解码JWT令牌
                secret_key = self.config_manager.security.encryption_key
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                token_user_id = payload.get("user_id")
                
                # 确保请求的用户ID与令牌中的用户ID匹配
                if str(token_user_id) != str(user_id):
                    return web.json_response({
                        "success": False,
                        "error": "无权访问其他用户的智能体"
                    }, status=403)
            except jwt.PyJWTError:
                return web.json_response({
                    "success": False,
                    "error": "无效的令牌"
                }, status=401)
            
            # 获取智能体详情
            agent = self.user_manager.get_agent_by_id(agent_id, user_id)
            
            if not agent:
                return web.json_response({
                    "success": False,
                    "error": "智能体不存在"
                }, status=404)
            
            return web.json_response({
                "success": True,
                "agent": agent
            })
        except Exception as e:
            logger.error(f"获取智能体详情时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "获取智能体详情失败"
            }, status=500)

    async def create_agent(self, request: web.Request) -> web.Response:
        """创建新的智能体实例"""
        try:
            # 从请求路径参数获取用户ID
            user_id = int(request.match_info.get('user_id'))
            
            # 从请求体获取数据
            data = await request.json()
            template_id = data.get('template_id', 'default-assistant')
            name = data.get('name')
            
            if not name:
                return web.json_response({
                    "success": False,
                    "error": "智能体名称是必填项"
                }, status=400)
            
            # 验证用户身份
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return web.json_response({
                    "success": False,
                    "error": "未提供认证令牌"
                }, status=401)
            
            token = auth_header.split(' ')[1]
            
            try:
                # 解码JWT令牌
                secret_key = self.config_manager.security.encryption_key
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                token_user_id = payload.get("user_id")
                
                # 确保请求的用户ID与令牌中的用户ID匹配
                if str(token_user_id) != str(user_id):
                    return web.json_response({
                        "success": False,
                        "error": "无权为其他用户创建智能体"
                    }, status=403)
            except jwt.PyJWTError:
                return web.json_response({
                    "success": False,
                    "error": "无效的令牌"
                }, status=401)
            
            # 创建智能体
            agent = self.user_manager.create_agent(
                user_id=user_id,
                template_id=template_id,
                name=name,
                avatar_url=data.get('avatar_url'),
                custom_system_prompt=data.get('custom_system_prompt'),
                selected_model=data.get('selected_model'),
                temperature=data.get('temperature', 0.7),
                memory_rounds=data.get('memory_rounds', 10)
            )
            
            if not agent:
                return web.json_response({
                    "success": False,
                    "error": "创建智能体失败"
                }, status=500)
            
            return web.json_response({
                "success": True,
                "agent": agent
            })
        except Exception as e:
            logger.error(f"创建智能体时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "创建智能体失败"
            }, status=500)

    async def update_agent(self, request: web.Request) -> web.Response:
        """更新智能体实例"""
        try:
            # 从请求路径参数获取用户ID和智能体ID
            user_id = int(request.match_info.get('user_id'))
            agent_id = int(request.match_info.get('agent_id'))
            
            # 从请求体获取数据
            data = await request.json()
            
            # 验证用户身份
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return web.json_response({
                    "success": False,
                    "error": "未提供认证令牌"
                }, status=401)
            
            token = auth_header.split(' ')[1]
            
            try:
                # 解码JWT令牌
                secret_key = self.config_manager.security.encryption_key
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                token_user_id = payload.get("user_id")
                
                # 确保请求的用户ID与令牌中的用户ID匹配
                if str(token_user_id) != str(user_id):
                    return web.json_response({
                        "success": False,
                        "error": "无权更新其他用户的智能体"
                    }, status=403)
            except jwt.PyJWTError:
                return web.json_response({
                    "success": False,
                    "error": "无效的令牌"
                }, status=401)
            
            # 更新智能体
            agent = self.user_manager.update_agent(
                agent_id=agent_id,
                user_id=user_id,
                name=data.get('name'),
                avatar_url=data.get('avatar_url'),
                custom_system_prompt=data.get('custom_system_prompt'),
                selected_model=data.get('selected_model'),
                temperature=data.get('temperature'),
                memory_rounds=data.get('memory_rounds'),
                is_active=data.get('is_active', True)
            )
            
            if not agent:
                return web.json_response({
                    "success": False,
                    "error": "更新智能体失败"
                }, status=500)
            
            return web.json_response({
                "success": True,
                "agent": agent
            })
        except Exception as e:
            logger.error(f"更新智能体时出错: {str(e)}")
            return web.json_response({
                "success": False,
                "error": "更新智能体失败"
            }, status=500)

    async def get_version(self, request):
        """获取API版本信息"""
        return web.json_response({
            "version": __version__,
            "service": "agency-core backend",
            "timestamp": datetime.now().isoformat()
        })

    async def setup_routes(self, app):
        """设置路由"""
        # 添加路由
        app.router.add_get('/api/health', self.health_check)
        app.router.add_get('/api/user/{user_id}/characters', self.list_characters)
        app.router.add_get('/api/character/{character_id}', self.get_character_detail)
        app.router.add_post('/api/user/{user_id}/characters', self.create_character)
        app.router.add_put('/api/character/{character_id}', self.update_character)
        app.router.add_delete('/api/user/{user_id}/characters/{character_id}', self.delete_character)
        app.router.add_post('/api/user/{user_id}/characters/{character_id}/switch', self.switch_character)
        app.router.add_get('/api/character/types', self.get_available_roles)
        app.router.add_get('/api/config', self.get_config)
        app.router.add_post('/api/chat/process', self.process_chat)
        
        # 认证相关路由
        app.router.add_post('/api/auth/register', self.register)
        app.router.add_post('/api/auth/login', self.login)
        app.router.add_post('/api/auth/request-password-reset', self.request_password_reset)  # 添加请求重置密码路由
        app.router.add_post('/api/auth/reset-password', self.reset_password)  # 添加重置密码路由
        app.router.add_get('/api/auth/me', self.get_current_user)
        
        # 智能体相关路由
        app.router.add_get('/api/user/{user_id}/agents', self.get_user_agents)
        app.router.add_post('/api/user/{user_id}/agents', self.create_agent)
        app.router.add_get('/api/user/{user_id}/agents/{agent_id}', self.get_agent_detail)
        app.router.add_put('/api/user/{user_id}/agents/{agent_id}', self.update_agent)
        
        # 版本相关路由
        app.router.add_get('/api/version', self.get_version)
        
        # 添加CORS中间件
        async def cors_middleware(app, handler):
            async def middleware(request):
                # 处理预检请求
                if request.method == "OPTIONS":
                    resp = web.Response()
                    resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = "*"
                    resp.headers[hdrs.ACCESS_CONTROL_ALLOW_HEADERS] = "Content-Type, Authorization"
                    resp.headers[hdrs.ACCESS_CONTROL_ALLOW_METHODS] = "POST, GET, DELETE, PUT, OPTIONS"
                    return resp
                
                # 处理实际请求
                response = await handler(request)
                response.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = "*"
                response.headers[hdrs.ACCESS_CONTROL_ALLOW_CREDENTIALS] = "true"
                return response
            return middleware
        
        app.middlewares.append(cors_middleware)
        
        return app

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
    app.router.add_post('/api/auth/request-password-reset', api_instance.request_password_reset)  # 添加请求重置密码路由
    app.router.add_post('/api/auth/reset-password', api_instance.reset_password)  # 添加重置密码路由
    app.router.add_get('/api/auth/me', api_instance.get_current_user)
    
    # 智能体相关路由
    app.router.add_get('/api/user/{user_id}/agents', api_instance.get_user_agents)
    app.router.add_post('/api/user/{user_id}/agents', api_instance.create_agent)
    app.router.add_get('/api/user/{user_id}/agents/{agent_id}', api_instance.get_agent_detail)
    app.router.add_put('/api/user/{user_id}/agents/{agent_id}', api_instance.update_agent)
    
    # 版本相关路由 - 添加版本API端点
    app.router.add_get('/api/version', api_instance.get_version)
    
    # 添加CORS中间件
    async def cors_middleware(app, handler):
        async def middleware(request):
            # 处理预检请求
            if request.method == "OPTIONS":
                resp = web.Response()
                resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = "*"
                resp.headers[hdrs.ACCESS_CONTROL_ALLOW_HEADERS] = "Content-Type, Authorization"
                resp.headers[hdrs.ACCESS_CONTROL_ALLOW_METHODS] = "POST, GET, DELETE, PUT, OPTIONS"
                return resp
            
            # 处理实际请求
            response = await handler(request)
            response.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = "*"
            response.headers[hdrs.ACCESS_CONTROL_ALLOW_CREDENTIALS] = "true"
            return response
        return middleware
    
    app.middlewares.append(cors_middleware)
    
    return app