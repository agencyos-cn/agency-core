"""配置管理器 - 按功能模块拆分的配置方式"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, fields

# 导入各模块的配置类和默认配置
from .core_config import CoreConfig, DEFAULT_CORE_CONFIG
from .llm_config import LLMConfig, DEFAULT_LLM_CONFIG
from .dify_config import DifyConfig, DEFAULT_DIFY_CONFIG
from .openclaw_config import OpenClawConfig, DEFAULT_OPENCLAW_CONFIG
from .security_config import SecurityConfig
from ..devices.device_config import DeviceConfig
from .database.database_config import DatabaseConfig
from .mail_config import MailConfig


class Config:
    def __init__(self, config_file: str = None):
        """Initialize config from file, with environment variable overrides"""
        self._config_data = self._load_config(config_file)
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load config from JSON file with environment variable overrides"""
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            # Default configuration
            config = self._get_default_config()
            
        # Override with environment variables
        self._apply_environment_overrides(config)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "core": {
                "service_name": "AgencyOS-Core",
                "host": "0.0.0.0",
                "port": 18789,
                "debug": False,
                "enable_third_party_ecosystem": True,
                "ecosystem_sync_interval": 1800,
                "external_services": {},
                "enable_service_discovery": True,
                "cache_enabled": True,
                "cache_ttl": 3600,
                "cache_backend": "memory",
                "log_level": "INFO",
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "log_file": None
            },
            "llm": {
                "local_model_enabled": False,
                "local_model_provider": "ollama",
                "local_model_name": "llama2",
                "local_api_base": "http://localhost:11434/v1",
                "local_api_key": "local-key",
                "providers": {
                    "openai": {
                        "api_key": "",
                        "model": "gpt-4",
                        "temperature": 0.7
                    },
                    "anthropic": {
                        "api_key": "",
                        "model": "claude-2",
                        "temperature": 0.7
                    },
                    "huggingface": {
                        "api_key": "",
                        "model": "meta-llama/Llama-2-7b-chat-hf",
                        "temperature": 0.7
                    },
                    "dify": {
                        "api_key": "",
                        "api_base": "",
                        "app_id": ""
                    },
                    "openclaw": {
                        "api_key": "",
                        "api_base": "",
                        "app_id": ""
                    }
                },
                "default_provider": "openai",
                "fallback_providers": [
                    "anthropic",
                    "huggingface",
                    "dify"
                ],
                "enable_model_fallback": True,
                "request_timeout": 30,
                "max_retries": 3,
                "third_party_models_enabled": True,
                "integrated_platforms": [
                    "dify",
                    "openclaw",
                    "huggingface",
                    "modelscope",
                    "openrouter",
                    "zhipu",
                    "aliyun",
                    "baidu",
                    "tencent"
                ],
                "model_marketplace_urls": {
                    "huggingface": "https://huggingface.co/models",
                    "modelscope": "https://modelscope.cn/models",
                    "dify": "https://dify.ai/templates",
                    "openclaw": "https://openclaw.ai/skills",
                    "openrouter": "https://openrouter.ai/models",
                    "zhipu": "https://open.bigmodel.cn/dev/howuse",
                    "aliyun": "https://www.aliyun.com/product/dashscope",
                    "baidu": "https://cloud.baidu.com/product/wenxin yi",
                    "tencent": "https://cloud.tencent.com/product/hunyu"
                }
            },
            "dify": {
                "api_base": "http://localhost:8765/v1",
                "api_key": "",
                "app_id": "",
                "third_party_llm_providers": {},
                "enable_remote_models": True,
                "external_skill_sources": [],
                "sync_external_skills": True,
                "skill_sync_interval": 3600,
                "model_cache_ttl": 3600,
                "skill_cache_ttl": 1800
            },
            "openclaw": {
                "api_base": "http://localhost:8080/v1",
                "api_key": "",
                "app_id": "",
                "third_party_llm_providers": {},
                "enable_remote_models": True,
                "external_skill_sources": [],
                "sync_external_skills": True,
                "skill_sync_interval": 3600,
                "channels": {},
                "enable_multi_channel": True,
                "model_cache_ttl": 3600,
                "skill_cache_ttl": 1800
            },
            "security": {
                "encryption_enabled": True,
                "encryption_key": "your-super-secret-jwt-signing-key-here",
                "access_control_enabled": True,
                "rate_limit_enabled": True,
                "max_requests_per_minute": 100,
                "ssl_enabled": False,
                "ssl_cert_file": "",
                "ssl_key_file": ""
            },
            "device": {
                "discovery_enabled": True,
                "supported_protocols": [
                    "tcp",
                    "udp",
                    "mqtt",
                    "http",
                    "websocket"
                ],
                "connection_timeout": 10,
                "reconnect_interval": 5,
                "max_connections": 100,
                "device_registry": {
                    "type": "memory",
                    "config": {}
                }
            },
            "database": {
                "host": "localhost",
                "port": 3306,
                "user": "agencyadmin",
                "password": "123456",
                "database": "agencyos_db",
                "charset": "utf8mb4",
                "pool_size": 10,
                "max_overflow": 20,
                "pool_recycle": 3600,
                "connect_timeout": 10,
                "read_timeout": 10,
                "write_timeout": 10,
                "ssl_enabled": False,
                "autocommit": False,
                "use_unicode": True
            }
        }
    
    def _apply_environment_overrides(self, config: Dict[str, Any]):
        """Apply environment variable overrides to config"""
        # Database configuration
        config['database']['host'] = os.getenv('DB_HOST', config['database'].get('host', 'localhost'))
        config['database']['port'] = int(os.getenv('DB_PORT', config['database'].get('port', 3306)))
        config['database']['user'] = os.getenv('DB_USER', config['database'].get('user', 'agencyadmin'))
        config['database']['password'] = os.getenv('DB_PASSWORD', config['database'].get('password', ''))
        config['database']['database'] = os.getenv('DB_NAME', config['database'].get('database', 'agencyos_db'))
        
        # Security configuration
        config['security']['encryption_key'] = os.getenv('ENCRYPTION_KEY', config['security'].get('encryption_key', ''))
        
        # LLM provider API keys
        config['llm']['providers']['openai']['api_key'] = os.getenv('OPENAI_API_KEY', config['llm']['providers']['openai'].get('api_key', ''))
        config['llm']['providers']['anthropic']['api_key'] = os.getenv('ANTHROPIC_API_KEY', config['llm']['providers']['anthropic'].get('api_key', ''))
        config['llm']['providers']['huggingface']['api_key'] = os.getenv('HUGGINGFACE_API_KEY', config['llm']['providers']['huggingface'].get('api_key', ''))
        config['llm']['providers']['dify']['api_key'] = os.getenv('DIFY_API_KEY', config['llm']['providers']['dify'].get('api_key', ''))
        config['llm']['providers']['openclaw']['api_key'] = os.getenv('OPENCLAW_API_KEY', config['llm']['providers']['openclaw'].get('api_key', ''))
        
        # Dify configuration
        config['dify']['api_base'] = os.getenv('DIFY_API_BASE', config['dify'].get('api_base', ''))
        config['dify']['api_key'] = os.getenv('DIFY_API_KEY', config['dify'].get('api_key', ''))
        config['dify']['app_id'] = os.getenv('DIFY_APP_ID', config['dify'].get('app_id', ''))
        
        # OpenClaw configuration
        config['openclaw']['api_base'] = os.getenv('OPENCLAW_API_BASE', config['openclaw'].get('api_base', ''))
        config['openclaw']['api_key'] = os.getenv('OPENCLAW_API_KEY', config['openclaw'].get('api_key', ''))
        config['openclaw']['app_id'] = os.getenv('OPENCLAW_APP_ID', config['openclaw'].get('app_id', ''))
        
        # Other configurations could be added here as needed
    
    def get(self, key: str, default=None):
        """Get a configuration value by key"""
        keys = key.split('.')
        value = self._config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def update(self, key: str, value):
        """Update a configuration value"""
        keys = key.split('.')
        config_ref = self._config_data
        
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
            
        config_ref[keys[-1]] = value

class ConfigManager:
    """配置管理器 - 统一管理所有配置"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.json"
        
        # 初始化各模块配置
        self.core = DEFAULT_CORE_CONFIG
        self.llm = DEFAULT_LLM_CONFIG
        self.dify = DEFAULT_DIFY_CONFIG
        self.openclaw = DEFAULT_OPENCLAW_CONFIG
        self.security = SecurityConfig()
        self.device = DeviceConfig()
        self.database = DatabaseConfig()  # 添加数据库配置
        self.mail = MailConfig()  # 添加邮件配置
        
        # 加载配置
        self.load_config()

    def load_config(self):
        """从文件加载配置"""
        try:
            # 首先尝试加载主配置文件
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 加载核心配置
                if 'core' in config_data:
                    self.core = CoreConfig(**config_data['core'])
                
                # 加载LLM配置
                if 'llm' in config_data:
                    self.llm = LLMConfig(**config_data['llm'])
                
                # 加载Dify配置
                if 'dify' in config_data:
                    self.dify = DifyConfig(**config_data['dify'])
                
                # 加载OpenClaw配置
                if 'openclaw' in config_data:
                    self.openclaw = OpenClawConfig(**config_data['openclaw'])
                
                # 加载安全配置
                if 'security' in config_data:
                    self.security = SecurityConfig(**config_data['security'])
                    
                # 加载设备配置
                if 'device' in config_data:
                    self.device = DeviceConfig(**config_data['device'])
                    
                # 加载数据库配置
                if 'database' in config_data:
                    self.database = DatabaseConfig(**config_data['database'])
            else:
                # 如果主配置文件不存在，尝试加载示例配置
                example_config = "config.example.json"
                if os.path.exists(example_config):
                    with open(example_config, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # 加载核心配置
                    if 'core' in config_data:
                        self.core = CoreConfig(**config_data['core'])
                    
                    # 加载LLM配置
                    if 'llm' in config_data:
                        self.llm = LLMConfig(**config_data['llm'])
                    
                    # 加载Dify配置
                    if 'dify' in config_data:
                        self.dify = DifyConfig(**config_data['dify'])
                    
                    # 加载OpenClaw配置
                    if 'openclaw' in config_data:
                        self.openclaw = OpenClawConfig(**config_data['openclaw'])
                    
                    # 加载安全配置
                    if 'security' in config_data:
                        self.security = SecurityConfig(**config_data['security'])
                        
                    # 加载设备配置
                    if 'device' in config_data:
                        self.device = DeviceConfig(**config_data['device'])
                        
                    # 加载数据库配置
                    if 'database' in config_data:
                        self.database = DatabaseConfig(**config_data['database'])
                        
        except Exception as e:
            print(f"Error loading config from {self.config_file}: {e}")
            # 继续使用默认配置
            
        # 从环境变量加载配置（优先级更高）
        self.load_from_env()
        
        # 从第三方生态加载配置
        self._load_third_party_configs()

    def load_from_env(self):
        """从环境变量加载配置"""
        # 核心配置
        if 'AGENCY_CORE_HOST' in os.environ:
            self.core.host = os.environ['AGENCY_CORE_HOST']
        if 'AGENCY_CORE_PORT' in os.environ:
            self.core.port = int(os.environ['AGENCY_CORE_PORT'])
        if 'AGENCY_CORE_DEBUG' in os.environ:
            self.core.debug = os.environ['AGENCY_CORE_DEBUG'].lower() == 'true'
        
        # 数据库配置
        if 'DB_HOST' in os.environ:
            self.database.host = os.environ['DB_HOST']
        if 'DB_PORT' in os.environ:
            self.database.port = int(os.environ['DB_PORT'])
        if 'DB_USER' in os.environ:
            self.database.user = os.environ['DB_USER']
        if 'DB_PASSWORD' in os.environ:
            self.database.password = os.environ['DB_PASSWORD']
        if 'DB_NAME' in os.environ:
            self.database.database = os.environ['DB_NAME']
        if 'DB_CHARSET' in os.environ:
            self.database.charset = os.environ['DB_CHARSET']
        
        # LLM配置
        if 'AGENCY_LLM_DEFAULT_PROVIDER' in os.environ:
            self.llm.default_provider = os.environ['AGENCY_LLM_DEFAULT_PROVIDER']
        if 'AGENCY_LLM_LOCAL_ENABLED' in os.environ:
            self.llm.local_model_enabled = os.environ['AGENCY_LLM_LOCAL_ENABLED'].lower() == 'true'
        
        # Dify配置
        if 'AGENCY_DIFY_API_BASE' in os.environ:
            self.dify.api_base = os.environ['AGENCY_DIFY_API_BASE']
        if 'AGENCY_DIFY_API_KEY' in os.environ:
            self.dify.api_key = os.environ['AGENCY_DIFY_API_KEY']
        if 'AGENCY_DIFY_APP_ID' in os.environ:
            self.dify.app_id = os.environ['AGENCY_DIFY_APP_ID']
        
        # OpenClaw配置
        if 'AGENCY_OPENCLAW_API_BASE' in os.environ:
            self.openclaw.api_base = os.environ['AGENCY_OPENCLAW_API_BASE']
        if 'AGENCY_OPENCLAW_API_KEY' in os.environ:
            self.openclaw.api_key = os.environ['AGENCY_OPENCLAW_API_KEY']
        if 'AGENCY_OPENCLAW_APP_ID' in os.environ:
            self.openclaw.app_id = os.environ['AGENCY_OPENCLAW_APP_ID']

    def get_character_specific_config(self, character_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """获取角色特定的配置"""
        if not character_config:
            return {
                "llm": self.llm,
                "dify": self.dify,
                "openclaw": self.openclaw
            }
        
        # 合并全局配置和角色特定配置
        result = {
            "llm": self.llm,
            "dify": self.dify,
            "openclaw": self.openclaw,
            "core": self.core,
            "security": self.security,
            "device": self.device,
            "database": self.database
        }
        
        # 如果角色有特定的LLM配置，覆盖全局配置
        if "llm" in character_config:
            char_llm_config = character_config["llm"]
            result["llm"] = LLMConfig(
                local_model_enabled=char_llm_config.get("local_model_enabled", self.llm.local_model_enabled),
                local_model_provider=char_llm_config.get("local_model_provider", self.llm.local_model_provider),
                local_model_name=char_llm_config.get("local_model_name", self.llm.local_model_name),
                local_api_base=char_llm_config.get("local_api_base", self.llm.local_api_base),
                local_api_key=char_llm_config.get("local_api_key", self.llm.local_api_key),
                providers=char_llm_config.get("providers", self.llm.providers),
                default_provider=char_llm_config.get("default_provider", self.llm.default_provider),
                fallback_providers=char_llm_config.get("fallback_providers", self.llm.fallback_providers),
                enable_model_fallback=char_llm_config.get("enable_model_fallback", self.llm.enable_model_fallback),
                request_timeout=char_llm_config.get("request_timeout", self.llm.request_timeout),
                max_retries=char_llm_config.get("max_retries", self.llm.max_retries),
                third_party_models_enabled=char_llm_config.get("third_party_models_enabled", self.llm.third_party_models_enabled),
                integrated_platforms=char_llm_config.get("integrated_platforms", self.llm.integrated_platforms),
                model_marketplace_urls=char_llm_config.get("model_marketplace_urls", self.llm.model_marketplace_urls)
            )
        
        # 如果角色有特定的Dify配置，覆盖全局配置
        if "dify" in character_config:
            char_dify_config = character_config["dify"]
            result["dify"] = DifyConfig(
                api_base=char_dify_config.get("api_base", self.dify.api_base),
                api_key=char_dify_config.get("api_key", self.dify.api_key),
                app_id=char_dify_config.get("app_id", self.dify.app_id),
                third_party_llm_providers=char_dify_config.get("third_party_llm_providers", self.dify.third_party_llm_providers),
                enable_remote_models=char_dify_config.get("enable_remote_models", self.dify.enable_remote_models),
                external_skill_sources=char_dify_config.get("external_skill_sources", self.dify.external_skill_sources),
                sync_external_skills=char_dify_config.get("sync_external_skills", self.dify.sync_external_skills),
                skill_sync_interval=char_dify_config.get("skill_sync_interval", self.dify.skill_sync_interval),
                model_cache_ttl=char_dify_config.get("model_cache_ttl", self.dify.model_cache_ttl),
                skill_cache_ttl=char_dify_config.get("skill_cache_ttl", self.dify.skill_cache_ttl)
            )
        
        # 如果角色有特定的OpenClaw配置，覆盖全局配置
        if "openclaw" in character_config:
            char_openclaw_config = character_config["openclaw"]
            result["openclaw"] = OpenClawConfig(
                api_base=char_openclaw_config.get("api_base", self.openclaw.api_base),
                api_key=char_openclaw_config.get("api_key", self.openclaw.api_key),
                app_id=char_openclaw_config.get("app_id", self.openclaw.app_id),
                third_party_llm_providers=char_openclaw_config.get("third_party_llm_providers", self.openclaw.third_party_llm_providers),
                enable_remote_models=char_openclaw_config.get("enable_remote_models", self.openclaw.enable_remote_models),
                external_skill_sources=char_openclaw_config.get("external_skill_sources", self.openclaw.external_skill_sources),
                sync_external_skills=char_openclaw_config.get("sync_external_skills", self.openclaw.sync_external_skills),
                skill_sync_interval=char_openclaw_config.get("skill_sync_interval", self.openclaw.skill_sync_interval),
                channels=char_openclaw_config.get("channels", self.openclaw.channels),
                enable_multi_channel=char_openclaw_config.get("enable_multi_channel", self.openclaw.enable_multi_channel),
                model_cache_ttl=char_openclaw_config.get("model_cache_ttl", self.openclaw.model_cache_ttl),
                skill_cache_ttl=char_openclaw_config.get("skill_cache_ttl", self.openclaw.skill_cache_ttl)
            )
        
        # 如果角色有特定的核心配置，覆盖全局配置
        if "core" in character_config:
            char_core_config = character_config["core"]
            result["core"] = CoreConfig(
                service_name=char_core_config.get("service_name", self.core.service_name),
                host=char_core_config.get("host", self.core.host),
                port=char_core_config.get("port", self.core.port),
                debug=char_core_config.get("debug", self.core.debug),
                enable_third_party_ecosystem=char_core_config.get("enable_third_party_ecosystem", self.core.enable_third_party_ecosystem),
                ecosystem_sync_interval=char_core_config.get("ecosystem_sync_interval", self.core.ecosystem_sync_interval),
                external_services=char_core_config.get("external_services", self.core.external_services),
                enable_service_discovery=char_core_config.get("enable_service_discovery", self.core.enable_service_discovery),
                cache_enabled=char_core_config.get("cache_enabled", self.core.cache_enabled),
                cache_ttl=char_core_config.get("cache_ttl", self.core.cache_ttl),
                cache_backend=char_core_config.get("cache_backend", self.core.cache_backend),
                log_level=char_core_config.get("log_level", self.core.log_level),
                log_format=char_core_config.get("log_format", self.core.log_format),
                log_file=char_core_config.get("log_file", self.core.log_file)
            )
            
        # 如果角色有特定的安全配置，覆盖全局配置
        if "security" in character_config:
            char_security_config = character_config["security"]
            result["security"] = SecurityConfig(
                encryption_enabled=char_security_config.get("encryption_enabled", self.security.encryption_enabled),
                encryption_key=char_security_config.get("encryption_key", self.security.encryption_key),
                access_control_enabled=char_security_config.get("access_control_enabled", self.security.access_control_enabled),
                rate_limit_enabled=char_security_config.get("rate_limit_enabled", self.security.rate_limit_enabled),
                max_requests_per_minute=char_security_config.get("max_requests_per_minute", self.security.max_requests_per_minute),
                ssl_enabled=char_security_config.get("ssl_enabled", self.security.ssl_enabled),
                ssl_cert_file=char_security_config.get("ssl_cert_file", self.security.ssl_cert_file),
                ssl_key_file=char_security_config.get("ssl_key_file", self.security.ssl_key_file),
                enforce_api_key_validation=char_security_config.get("enforce_api_key_validation", self.security.enforce_api_key_validation),
                api_key_storage_encrypted=char_security_config.get("api_key_storage_encrypted", self.security.api_key_storage_encrypted),
                api_key_expiry_days=char_security_config.get("api_key_expiry_days", self.security.api_key_expiry_days),
                enable_rbac=char_security_config.get("enable_rbac", self.security.enable_rbac),
                default_user_role=char_security_config.get("default_user_role", self.security.default_user_role),
                allowed_origins=char_security_config.get("allowed_origins", self.security.allowed_origins),
                encrypt_sensitive_data=char_security_config.get("encrypt_sensitive_data", self.security.encrypt_sensitive_data),
                encryption_algorithm=char_security_config.get("encryption_algorithm", self.security.encryption_algorithm),
                encryption_key_path=char_security_config.get("encryption_key_path", self.security.encryption_key_path),
                enable_audit_logging=char_security_config.get("enable_audit_logging", self.security.enable_audit_logging),
                audit_log_retention_days=char_security_config.get("audit_log_retention_days", self.security.audit_log_retention_days),
                enable_rate_limiting=char_security_config.get("enable_rate_limiting", self.security.enable_rate_limiting),
                rate_limit_requests=char_security_config.get("rate_limit_requests", self.security.rate_limit_requests),
                rate_limit_window=char_security_config.get("rate_limit_window", self.security.rate_limit_window),
                enable_input_sanitization=char_security_config.get("enable_input_sanitization", self.security.enable_input_sanitization),
                max_request_size=char_security_config.get("max_request_size", self.security.max_request_size),
                enable_security_headers=char_security_config.get("enable_security_headers", self.security.enable_security_headers),
                enable_vulnerability_scanning=char_security_config.get("enable_vulnerability_scanning", self.security.enable_vulnerability_scanning)
            )
            
        # 如果角色有特定的设备配置，覆盖全局配置
        if "device" in character_config:
            char_device_config = character_config["device"]
            result["device"] = DeviceConfig(
                discovery_enabled=char_device_config.get("discovery_enabled", self.device.discovery_enabled),
                supported_protocols=char_device_config.get("supported_protocols", self.device.supported_protocols),
                reconnect_interval=char_device_config.get("reconnect_interval", self.device.reconnect_interval),
                scan_interval=char_device_config.get("scan_interval", self.device.scan_interval),
                connection_timeout=char_device_config.get("connection_timeout", self.device.connection_timeout),
                retry_attempts=char_device_config.get("retry_attempts", self.device.retry_attempts),
                max_connections=char_device_config.get("max_connections", self.device.max_connections),
                enable_discovery=char_device_config.get("enable_discovery", self.device.enable_discovery),
                discovery_methods=char_device_config.get("discovery_methods", self.device.discovery_methods),
                discovery_timeout=char_device_config.get("discovery_timeout", self.device.discovery_timeout),
                auth_required=char_device_config.get("auth_required", self.device.auth_required),
                auth_timeout=char_device_config.get("auth_timeout", self.device.auth_timeout),
                connection_pool_size=char_device_config.get("connection_pool_size", self.device.connection_pool_size),
                keep_alive=char_device_config.get("keep_alive", self.device.keep_alive),
                keep_alive_interval=char_device_config.get("keep_alive_interval", self.device.keep_alive_interval),
                allow_untrusted_certs=char_device_config.get("allow_untrusted_certs", self.device.allow_untrusted_certs),
                encryption_enabled=char_device_config.get("encryption_enabled", self.device.encryption_enabled),
                device_specific_configs=char_device_config.get("device_specific_configs", self.device.device_specific_configs),
                device_registry=char_device_config.get("device_registry", self.device.device_registry)
            )
            
        # 如果角色有特定的数据库配置，覆盖全局配置
        if "database" in character_config:
            char_database_config = character_config["database"]
            result["database"] = DatabaseConfig(
                host=char_database_config.get("host", self.database.host),
                port=char_database_config.get("port", self.database.port),
                user=char_database_config.get("user", self.database.user),
                password=char_database_config.get("password", self.database.password),
                database=char_database_config.get("database", self.database.database),
                charset=char_database_config.get("charset", self.database.charset),
                pool_size=char_database_config.get("pool_size", self.database.pool_size),
                max_overflow=char_database_config.get("max_overflow", self.database.max_overflow),
                pool_recycle=char_database_config.get("pool_recycle", self.database.pool_recycle),
                connect_timeout=char_database_config.get("connect_timeout", self.database.connect_timeout),
                read_timeout=char_database_config.get("read_timeout", self.database.read_timeout),
                write_timeout=char_database_config.get("write_timeout", self.database.write_timeout),
                ssl_enabled=char_database_config.get("ssl_enabled", self.database.ssl_enabled),
                ssl_ca=char_database_config.get("ssl_ca", self.database.ssl_ca),
                ssl_cert=char_database_config.get("ssl_cert", self.database.ssl_cert),
                ssl_key=char_database_config.get("ssl_key", self.database.ssl_key),
                autocommit=char_database_config.get("autocommit", self.database.autocommit),
                use_unicode=char_database_config.get("use_unicode", self.database.use_unicode)
            )
        
        return result

    def _load_third_party_configs(self):
        """从第三方生态加载配置"""
        # 启用第三方生态
        self.core.enable_third_party_ecosystem = True
        
        # 设置默认的第三方提供商
        if not self.llm.providers:
            self.llm.providers = {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "model": "gpt-4"
                },
                "anthropic": {
                    "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                    "model": "claude-2"
                },
                "dify": {
                    "api_key": self.dify.api_key,
                    "api_base": self.dify.api_base
                },
                "openclaw": {
                    "api_key": self.openclaw.api_key,
                    "api_base": self.openclaw.api_base
                }
            }
        
        # 设置降级提供商
        if not self.llm.fallback_providers:
            self.llm.fallback_providers = ["anthropic", "google", "dify"]

    def save_config(self):
        """保存配置到文件"""
        config_data = {
            "core": self.core.__dict__,
            "llm": self.llm.__dict__,
            "dify": self.dify.__dict__,
            "openclaw": self.openclaw.__dict__,
            "security": self.security.__dict__,
            "device": self.device.__dict__,
            "database": self.database.__dict__
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    def has_llm_config(self) -> bool:
        """检查是否有有效的LLM配置"""
        return (
            self.llm.local_model_enabled or 
            (self.llm.providers and 
             any(provider.get("api_key") for provider in self.llm.providers.values() if self.llm.providers))
        )
    
    def has_dify_config(self) -> bool:
        """检查是否有有效的Dify配置"""
        # 检查是否有API密钥和API基础URL
        return self.dify.api_key != "" and self.dify.api_base != "http://localhost:8765/v1"
    
    def has_openclaw_config(self) -> bool:
        """检查是否有有效的OpenClaw配置"""
        # 检查是否有API密钥和API基础URL
        return self.openclaw.api_key != "" and self.openclaw.api_base != "http://localhost:8080/v1"

    def _config_to_dict(self, config_obj: Any) -> Dict[str, Any]:
        """将配置对象转换为字典"""
        result = {}
        for field in fields(config_obj):
            value = getattr(config_obj, field.name)
            result[field.name] = value
        return result

    def get_active_llm_provider(self) -> str:
        """获取当前活跃的LLM提供商"""
        # 如果本地模型启用且配置完成，则优先使用本地模型
        if (self.llm.local_model_enabled and 
            self.llm.local_api_key and 
            self.llm.local_api_key != "local-key"):
            return "local"
        
        # 否则返回默认提供商
        return self.llm.default_provider

    def get_available_models(self) -> Dict[str, Any]:
        """获取可用的模型列表"""
        models = {}
        
        # 添加本地模型
        if self.llm.local_model_enabled:
            models["local"] = {
                "provider": self.llm.local_model_provider,
                "model": self.llm.local_model_name,
                "endpoint": self.llm.local_api_base
            }
        
        # 添加第三方提供商的模型
        if self.llm.providers:
            for provider_name, provider_config in self.llm.providers.items():
                if provider_config.get("api_key"):  # 只有配置了API密钥的提供商才可用
                    models[provider_name] = provider_config
        
        return models

    def get_third_party_ecosystem_status(self) -> Dict[str, bool]:
        """获取第三方生态集成状态"""
        return {
            "dify_connected": bool(self.dify.api_key),
            "openclaw_connected": bool(self.openclaw.api_key),
            "external_skills_synced": self.dify.sync_external_skills or self.openclaw.sync_external_skills,
            "remote_models_enabled": self.llm.third_party_models_enabled
        }
