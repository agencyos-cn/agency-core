from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import hashlib
import secrets


class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    password_hash: str
    role: str = "user"
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
        stored_pwd, salt = hashed_password.split(':')
        pwdhash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('ascii'), 100000)
        return pwdhash.hex() == stored_pwd


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None