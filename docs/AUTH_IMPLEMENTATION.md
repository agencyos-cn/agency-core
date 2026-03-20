# AgencyOS 后端用户认证功能实现指南

## 1. 数据库设计

首先需要在AgencyOS后端项目中添加用户认证相关的数据库表。

### 1.1 用户表 (users)

在 `/Users/Joye/Sites/AgencyOs/agency-core/src/core/database/models.py` 中添加：

```python
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
```

### 1.2 用户管理器 (User Manager)

创建 `/Users/Joye/Sites/AgencyOs/agency-core/src/core/auth/user_manager.py`：

```python
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
        encoded_jwt = jwt.encode(to_encode, self.config.security.encryption_key, algorithm="HS256")
        return encoded_jwt
```

## 2. 更新API路由

修改 `/Users/Joye/Sites/AgencyOs/agency-core/src/web/api.py` 添加认证相关路由：

```python
# 在文件顶部添加导入
from src.core.auth.user_manager import UserManager, Token
import jwt
from datetime import timedelta

# 在WebAPI类中添加以下方法：

@routes.post('/api/auth/register')
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

@routes.post('/api/auth/login')
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

@routes.get('/api/auth/me')
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
            payload = jwt.decode(token, self.config.security.encryption_key, algorithms=["HS256"])
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
        
        user_manager = UserManager()
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
```

## 3. 配置加密密钥

在 `/Users/Joye/Sites/AgencyOs/agency-core/config.example.json` 中添加加密密钥：

```json
{
  // ... 其他配置 ...
  "security": {
    "encryption_enabled": true,
    "encryption_key": "your-super-secret-jwt-signing-key-here",  // 替换为实际的密钥
    "access_control_enabled": true,
    "rate_limit_enabled": true,
    "max_requests_per_minute": 100,
    "ssl_enabled": false,
    "ssl_cert_file": "",
    "ssl_key_file": ""
  }
  // ... 其他配置 ...
}
```

## 4. 更新前端环境配置

在前端项目 `/Users/Joye/Sites/AgencyOs/agencyos-user-panel/.env` 中设置后端API基础URL：

```
VITE_API_BASE_URL=http://localhost:18789/api
```

## 5. 启动后端服务

确保安装了必要的依赖：

```bash
cd /Users/Joye/Sites/AgencyOs/agency-core
pip install pyjwt cryptography
```

启动后端服务：

```bash
cd /Users/Joye/Sites/AgencyOs/agencyos-user-panel
npm run dev
```

然后在另一个终端中启动后端服务：

```bash
cd /Users/Joye/Sites/AgencyOs/agency-core
python main.py
```

## 6. 测试API端点

注册用户:
```bash
curl -X POST http://localhost:18789/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"测试用户","email":"test@example.com","password":"password123"}'
```

登录用户:
```bash
curl -X POST http://localhost:18789/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

获取当前用户:
```bash
curl -X GET http://localhost:18789/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```