import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional
from src.core.database.models import User
from src.core.config import ConfigManager
import pymysql
from pymysql import Error
import hashlib
import secrets


class UserManager:
    def __init__(self):
        self.config = ConfigManager()
        self.secret_key = self.config.security.encryption_key
        # 使用配置中的数据库连接参数
        db_config = self.config.database
        self.connection_params = {
            'host': db_config.host,
            'port': db_config.port,
            'user': db_config.user,
            'password': db_config.password,
            'database': db_config.database,
            'charset': db_config.charset,
            'connect_timeout': db_config.connect_timeout,
            'read_timeout': db_config.read_timeout,
            'write_timeout': db_config.write_timeout
        }
        self._init_db()

    def get_connection(self):
        """获取数据库连接"""
        return pymysql.connect(**self.connection_params)

    def _init_db(self):
        """初始化数据库表"""
        connection = None
        cursor = None
        try:
            # 连接到数据库（注意：这里我们连接到具体的数据库而不是information_schema系统数据库）
            connection = pymysql.connect(
                host=self.connection_params['host'],
                port=self.connection_params['port'],
                user=self.connection_params['user'],
                password=self.connection_params['password'],
                charset=self.connection_params['charset']
            )
            
            cursor = connection.cursor()
            
            # 选择数据库或创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.connection_params['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE {self.connection_params['database']}")
            
            # 创建用户表（如果不存在）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
                    email VARCHAR(255) UNIQUE NOT NULL COMMENT '登录邮箱',
                    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
                    nickname VARCHAR(100) COMMENT '用户昵称',
                    avatar_url VARCHAR(500) COMMENT '用户头像',
                    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active' COMMENT '账号状态',
                    last_login TIMESTAMP NULL COMMENT '最后登录时间',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    INDEX idx_email (email) COMMENT '邮箱登录索引',
                    INDEX idx_status (status) COMMENT '状态查询索引',
                    INDEX idx_created (created_at) COMMENT '注册时间索引'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表'
            """)
            
            # 创建角色表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    permissions JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # 创建智能体实例表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_agents (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '智能体实例ID',
                    user_id BIGINT NOT NULL COMMENT '所属用户ID',
                    template_id VARCHAR(64) NOT NULL COMMENT '基于哪个模板创建',
                    name VARCHAR(100) NOT NULL COMMENT '用户自定义名称',
                    avatar_url VARCHAR(500) COMMENT '自定义头像（覆盖模板）',
                    custom_system_prompt TEXT COMMENT '自定义提示词（覆盖模板）',
                    selected_model VARCHAR(100) COMMENT '用户选择的模型（覆盖模板）',
                    temperature DECIMAL(2,1) DEFAULT 0.7 COMMENT '温度设置（覆盖模板）',
                    memory_rounds INT DEFAULT 10 COMMENT '短期记忆轮数',
                    long_term_memory TEXT COMMENT '长期记忆内容（用户画像）',
                    memory_ttl INT DEFAULT 30 COMMENT '短期记忆保留天数',
                    is_active BOOLEAN DEFAULT true COMMENT '是否启用',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (template_id) REFERENCES platform_role_templates(id),
                    INDEX idx_user (user_id) COMMENT '按用户查询索引'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户智能体实例表'
            """)

            # 创建对话会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '会话ID',
                    agent_id BIGINT NOT NULL COMMENT '智能体ID',
                    title VARCHAR(200) COMMENT '会话标题',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
                    FOREIGN KEY (agent_id) REFERENCES user_agents(id) ON DELETE CASCADE,
                    INDEX idx_agent (agent_id) COMMENT '按智能体查询会话',
                    INDEX idx_created (created_at) COMMENT '按创建时间查询'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话会话表'
            """)

            # 创建对话消息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
                    conversation_id BIGINT NOT NULL COMMENT '所属会话ID',
                    role ENUM('user', 'assistant', 'system') NOT NULL COMMENT '消息角色',
                    content TEXT NOT NULL COMMENT '消息内容',
                    metadata JSON COMMENT '元数据（如引用来源、技能调用等）',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                    INDEX idx_conversation (conversation_id, created_at) COMMENT '按会话查询消息'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话消息表'
            """)

            # 检查是否有管理员账户，如果没有则创建
            cursor.execute("SELECT id FROM users WHERE email = %s", ("admin@agencyos.local",))
            if cursor.fetchone() is None:
                # 插入默认管理员用户 (密码是'password123'的哈希)
                password_hash = User.hash_password("password123")
                cursor.execute(
                    "INSERT IGNORE INTO users (email, password_hash, nickname, status) VALUES (%s, %s, %s, %s)",
                    ("admin@agencyos.local", password_hash, "Admin User", "active")
                )

            connection.commit()
            logging.info("Database initialized successfully")

        except Error as e:
            logging.error(f"Error initializing database: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def _tables_exist(self):
        """检查数据库表是否已经存在"""
        try:
            connection = pymysql.connect(
                host=self.connection_params['host'],
                port=self.connection_params['port'],
                user=self.connection_params['user'],
                password=self.connection_params['password'],
                database=self.connection_params['database']
            )
            
            cursor = connection.cursor()
            
            # 检查关键表是否存在
            cursor.execute("SHOW TABLES LIKE 'users'")
            users_exists = cursor.fetchone() is not None
            
            cursor.execute("SHOW TABLES LIKE 'user_agents'")
            agents_exists = cursor.fetchone() is not None
            
            cursor.execute("SHOW TABLES LIKE 'conversations'")
            conversations_exists = cursor.fetchone() is not None
            
            cursor.execute("SHOW TABLES LIKE 'messages'")
            messages_exists = cursor.fetchone() is not None
            
            # 如果所有关键表都存在，则认为数据库已初始化
            all_tables_exist = users_exists and agents_exists and conversations_exists and messages_exists
            
            return all_tables_exist
            
        except Error:
            # 如果无法连接或出现错误，假定表不存在
            return False
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    def create_user(self, name: str, email: str, password: str) -> Optional[User]:
        """创建新用户"""
        password_hash = User.hash_password(password)
        try:
            connection = self.get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            cursor.execute(
                "INSERT INTO users (email, password_hash, nickname) VALUES (%s, %s, %s)",
                (email, password_hash, name)
            )
            connection.commit()

            user_id = cursor.lastrowid
            cursor.execute(
                "SELECT id, email, nickname, password_hash, status, created_at, updated_at, avatar_url, last_login FROM users WHERE id = %s",
                (user_id,)
            )
            user_data = cursor.fetchone()

            return User(
                id=user_data['id'],
                email=user_data['email'],
                nickname=user_data['nickname'],
                password_hash=user_data['password_hash'],
                status=user_data['status'],
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at'],
                avatar_url=user_data['avatar_url'],
                last_login=user_data['last_login']
            )
        except Error as e:
            logging.error(f"Error creating user: {e}")
            return None
        finally:
            if connection:
                cursor.close()
                connection.close()

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        connection = self.get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute(
            "SELECT id, email, nickname, password_hash, status, created_at, updated_at, avatar_url, last_login FROM users WHERE email = %s AND status = 'active'",
            (email,)
        )
        row = cursor.fetchone()
        
        if row:
            user_data = {
                "id": row["id"],
                "email": row["email"],
                "nickname": row["nickname"] or row["email"].split('@')[0],  # 使用邮箱用户名部分作为昵称
                "password_hash": row["password_hash"],
                "status": row["status"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "avatar_url": row["avatar_url"],
                "last_login": row["last_login"]
            }
            user = User(**user_data)
            
            try:
                if User.verify_password(password, user.password_hash):
                    # 更新最后登录时间
                    update_cursor = connection.cursor()
                    update_cursor.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                        (user.id,)
                    )
                    connection.commit()
                    update_cursor.close()
                    
                    return user
            except ValueError:
                # 处理密码哈希格式不正确的情况
                print(f"密码哈希格式错误: {user.email}")
                return None
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        connection = self.get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute(
            "SELECT id, email, nickname, password_hash, status, created_at, updated_at, avatar_url, last_login FROM users WHERE email = %s AND status = 'active'",
            (email,)
        )
        row = cursor.fetchone()
        
        if row:
            user_data = {
                "id": row["id"],
                "email": row["email"],
                "nickname": row["nickname"] or row["email"].split('@')[0],
                "password_hash": row["password_hash"],
                "status": row["status"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "avatar_url": row["avatar_url"],
                "last_login": row["last_login"]
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