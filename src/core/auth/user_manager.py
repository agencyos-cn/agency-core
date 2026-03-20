import jwt
from datetime import datetime, timedelta
from typing import Optional
from src.core.database.models import User
from src.core.config import ConfigManager
import pymysql
from pymysql import Error
import logging
import os


class UserManager:
    def __init__(self):
        self.config = ConfigManager()
        self.secret_key = os.getenv('ENCRYPTION_KEY', self.config.security.encryption_key)
        self.db_config = self._get_db_config()
        
    def _get_db_config(self):
        """Get database configuration from environment variables or config"""
        return {
            'host': os.getenv('DB_HOST', self.config.database.host),
            'port': int(os.getenv('DB_PORT', self.config.database.port)),
            'user': os.getenv('DB_USER', self.config.database.user),
            'password': os.getenv('DB_PASSWORD', self.config.database.password),
            'database': os.getenv('DB_NAME', self.config.database.database),
            'charset': self.config.database.charset,
            'connect_timeout': self.config.database.connect_timeout,
            'read_timeout': self.config.database.read_timeout,
            'write_timeout': self.config.database.write_timeout
        }
        
    def get_connection(self):
        """获取数据库连接"""
        try:
            connection = pymysql.connect(**self.db_config)
            return connection
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            raise

    def initialize_database(self, force_init=False):
        """初始化数据库表"""
        if not force_init:
            # 检查是否已经有表存在
            if self._tables_exist():
                logging.info("Database tables already exist, skipping initialization")
                return
        
        # 连接到MySQL服务器（不指定数据库）
        db_config = self._get_db_config()
        connection = None
        cursor = None
        try:
            server_config = db_config.copy()
            server_config.pop('database', None)  # Remove database from config
            connection = pymysql.connect(**server_config)

            cursor = connection.cursor()

            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

            # 使用数据库
            cursor.execute(f"USE {db_config['database']}")

            # 创建用户表
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
                    INDEX idx_status (status) COMMENT '状态查询索引'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表'
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
                    INDEX idx_user (user_id) COMMENT '按用户查询索引'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户智能体实例表'
            """)

            logging.info("Database and tables initialized successfully")
        except Error as e:
            logging.error(f"Error initializing database: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def _tables_exist(self):
        """检查数据库表是否已存在"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # 检查 users 表是否存在
            cursor.execute("SHOW TABLES LIKE 'users'")
            users_table_exists = cursor.fetchone() is not None
            
            # 检查 user_agents 表是否存在
            cursor.execute("SHOW TABLES LIKE 'user_agents'")
            user_agents_table_exists = cursor.fetchone() is not None
            
            return users_table_exists and user_agents_table_exists
        except Exception as e:
            logging.error(f"Error checking if tables exist: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def create_user(self, email: str, password: str, nickname: str = None) -> Optional[User]:
        """创建新用户"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            password_hash = User.hash_password(password)
            
            # 设置默认昵称为邮箱前缀
            if not nickname:
                nickname = email.split('@')[0]
            
            cursor.execute(
                "INSERT INTO users (email, password_hash, nickname) VALUES (%s, %s, %s)",
                (email, password_hash, nickname)
            )
            user_id = cursor.lastrowid
            connection.commit()
            
            # 创建用户成功后立即创建一个默认智能体
            self._create_default_agent_for_user(connection, user_id, nickname)
            
            return User(
                id=user_id,
                email=email,
                password_hash=password_hash,
                nickname=nickname,
                status="active"
            )
        except pymysql.IntegrityError:
            # 邮箱已存在
            return None
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def _create_default_agent_for_user(self, connection, user_id: int, nickname: str):
        """为新用户创建一个默认智能体"""
        cursor = None
        try:
            cursor = connection.cursor()
            
            # 插入一个默认智能体
            cursor.execute(
                """
                INSERT INTO user_agents (user_id, template_id, name, avatar_url, custom_system_prompt, selected_model, temperature, memory_rounds)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, "default-assistant", f"{nickname}的助手", None, None, "gpt-3.5-turbo", 0.7, 10)
            )
            connection.commit()
        except Exception as e:
            logging.error(f"Error creating default agent for user: {e}")
        finally:
            if cursor:
                cursor.close()

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute("SELECT id, email, password_hash, nickname, status FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            
            if row and User.verify_password(password, row['password_hash']):
                # 更新最后登录时间
                self._update_last_login(connection, row['id'])
                
                return User(
                    id=row['id'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    nickname=row['nickname'],
                    status=row['status']
                )
        
        except Exception as e:
            logging.error(f"Error authenticating user: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return None

    def _update_last_login(self, connection, user_id: int):
        """更新用户的最后登录时间"""
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                (user_id,)
            )
            connection.commit()
        except Exception as e:
            logging.error(f"Error updating last login time: {e}")
        finally:
            if cursor:
                cursor.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute("SELECT id, email, password_hash, nickname, status FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            
            if row:
                return User(
                    id=row['id'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    nickname=row['nickname'],
                    status=row['status']
                )
        
        except Exception as e:
            logging.error(f"Error getting user by email: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute("SELECT id, email, password_hash, nickname, status FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return User(
                    id=row['id'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    nickname=row['nickname'],
                    status=row['status']
                )
        
        except Exception as e:
            logging.error(f"Error getting user by ID: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return None

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm="HS256")
        return encoded_jwt

    def get_user_agents(self, user_id: int):
        """获取用户的所有智能体实例"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute(
                """
                SELECT id, user_id, template_id, name, avatar_url, 
                       custom_system_prompt, selected_model, temperature, 
                       memory_rounds, long_term_memory, is_active, 
                       created_at, updated_at
                FROM user_agents 
                WHERE user_id = %s AND is_active = TRUE
                ORDER BY created_at DESC
                """, 
                (user_id,)
            )
            rows = cursor.fetchall()
            
            return rows
        except Exception as e:
            logging.error(f"Error getting user agents: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_agent_by_id(self, agent_id: int, user_id: int):
        """获取特定智能体实例"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute(
                """
                SELECT id, user_id, template_id, name, avatar_url, 
                       custom_system_prompt, selected_model, temperature, 
                       memory_rounds, long_term_memory, is_active, 
                       created_at, updated_at
                FROM user_agents 
                WHERE id = %s AND user_id = %s
                """, 
                (agent_id, user_id)
            )
            row = cursor.fetchone()
            
            return row
        except Exception as e:
            logging.error(f"Error getting agent by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def create_agent(self, user_id: int, template_id: str, name: str, 
                     avatar_url: str = None, custom_system_prompt: str = None, 
                     selected_model: str = None, temperature: float = 0.7, 
                     memory_rounds: int = 10):
        """创建新的智能体实例"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                INSERT INTO user_agents (
                    user_id, template_id, name, avatar_url, 
                    custom_system_prompt, selected_model, temperature, 
                    memory_rounds
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, template_id, name, avatar_url, custom_system_prompt, 
                 selected_model, temperature, memory_rounds)
            )
            agent_id = cursor.lastrowid
            connection.commit()
            
            return self.get_agent_by_id(agent_id, user_id)
        except Exception as e:
            logging.error(f"Error creating agent: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_agent(self, agent_id: int, user_id: int, **kwargs):
        """更新智能体实例"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # 构建动态更新查询
            update_fields = []
            values = []
            for field in ['name', 'avatar_url', 'custom_system_prompt', 
                         'selected_model', 'temperature', 'memory_rounds', 'is_active']:
                if field in kwargs:
                    update_fields.append(f"{field} = %s")
                    values.append(kwargs[field])
            
            if not update_fields:
                return None
                
            query = f"UPDATE user_agents SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
            values.extend([agent_id, user_id])
            
            cursor.execute(query, values)
            connection.commit()
            
            return self.get_agent_by_id(agent_id, user_id)
        except Exception as e:
            logging.error(f"Error updating agent: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()