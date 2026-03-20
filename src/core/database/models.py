from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import hashlib
import secrets


class User(BaseModel):
    id: Optional[int] = None
    email: str
    password_hash: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    status: str = "active"
    last_login: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """对密码进行哈希处理"""
        salt = secrets.token_hex(16)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('ascii'), 100000)
        pwdhash = pwdhash.hex()
        return f"{pwdhash}:{salt}"
    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            stored_pwd, salt = hashed_password.split(':')
            pwdhash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('ascii'), 100000)
            return pwdhash.hex() == stored_pwd
        except ValueError:
            # 如果密码哈希格式不正确（没有冒号分割），返回False
            return False


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# 新增模型类
class PlatformRoleTemplate(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    default_model: Optional[str] = None
    default_temperature: float = 0.7
    default_memory_rounds: int = 10
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class UserAgent(BaseModel):
    id: Optional[int] = None
    user_id: int
    template_id: str
    name: str
    avatar_url: Optional[str] = None
    custom_system_prompt: Optional[str] = None
    selected_model: Optional[str] = None
    temperature: float = 0.7
    memory_rounds: int = 10
    long_term_memory: Optional[str] = None
    memory_ttl: int = 30
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class KnowledgeBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    owner_type: str  # 'platform' or 'user'
    owner_id: Optional[int] = None
    file_url: Optional[str] = None
    vector_config: Optional[dict] = None
    is_public: bool = False
    status: str = "active"
    created_at: datetime


class Conversation(BaseModel):
    id: Optional[int] = None
    agent_id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class Message(BaseModel):
    id: Optional[int] = None
    conversation_id: int
    role: str  # 'user', 'assistant', or 'system'
    content: str
    metadata: Optional[dict] = None
    created_at: datetime