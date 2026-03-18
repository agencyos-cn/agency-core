import jwt
from datetime import datetime, timedelta
from typing import Optional
from src.core.database.models import User
from src.core.config import ConfigManager
import sqlite3
import os


class UserManager:
    def __init__(self, db_path: str = "agencyos.db"):
        self.db_path = db_path
        self.config = ConfigManager()
        self.secret_key = self.config.security.encryption_key
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, name: str, email: str, password: str) -> Optional[User]:
        """创建新用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = User.hash_password(password)
        
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            user_id = cursor.lastrowid
            conn.commit()
            
            return User(
                id=user_id,
                name=name,
                email=email,
                password_hash=password_hash
            )
        except sqlite3.IntegrityError:
            # 邮箱已存在
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        if row:
            user_data = {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "password_hash": row[3]
            }
            user = User(**user_data)
            
            if User.verify_password(password, user.password_hash):
                return user
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, email, password_hash, role FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        if row:
            user_data = {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4]
            }
            return User(**user_data)
        
        return None
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm="HS256")
        return encoded_jwt