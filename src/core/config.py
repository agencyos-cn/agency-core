"""配置管理器 - 按功能模块拆分的配置方式"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, fields
from .core_config import DEFAULT_CORE_CONFIG, CoreConfig
from .llm_config import DEFAULT_LLM_CONFIG, LLMConfig
from .dify_config import DEFAULT_DIFY_CONFIG, DifyConfig
from .openclaw_config import DEFAULT_OPENCLAW_CONFIG, OpenClawConfig
from .security_config import SecurityConfig
from ..devices.device_config import DeviceConfig


class ConfigManager:
    """配置管理器 - 统一管理所有配置"""
    
    def __init__(self, config_file: Optional[str] = None):
        # 初始化各模块配置
        self.core = DEFAULT_CORE_CONFIG
        self.llm = DEFAULT_LLM_CONFIG
        self.dify = DEFAULT_DIFY_CONFIG
        self.openclaw = DEFAULT_OPENCLAW_CONFIG
        self.security = SecurityConfig()  # 使用默认构造函数
        self.device = DeviceConfig()  # 使用默认构造函数
        
        # 从配置文件加载配置
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        # 从环境变量加载配置（优先级更高）
        self.load_from_env()
        
        # 从第三方生态加载配置
        self._load_third_party_configs()

    def load_from_file(self, config_file: str):
        """从JSON文件加载配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 更新各模块配置
        self._update_config_from_dict(self.core, config_data.get('core', {}))
        self._update_config_from_dict(self.llm, config_data.get('llm', {}))
        self._update_config_from_dict(self.dify, config_data.get('dify', {}))
        self._update_config_from_dict(self.openclaw, config_data.get('openclaw', {}))
        self._update_config_from_dict(self.security, config_data.get('security', {}))
        self._update_config_from_dict(self.device, config_data.get('device', {}))

    def load_from_env(self):
        """从环境变量加载配置"""
        # 核心配置
        if 'AGENCY_CORE_HOST' in os.environ:
            self.core.host = os.environ['AGENCY_CORE_HOST']
        if 'AGENCY_CORE_PORT' in os.environ:
            self.core.port = int(os.environ['AGENCY_CORE_PORT'])
        if 'AGENCY_CORE_DEBUG' in os.environ:
            self.core.debug = os.environ['AGENCY_CORE_DEBUG'].lower() == 'true'
        
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

    def _update_config_from_dict(self, config_obj: Any, config_dict: Dict[str, Any]):
        """从字典更新配置对象"""
        for key, value in config_dict.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)

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

    def save_to_file(self, config_file: str):
        """保存配置到文件"""
        config_data = {
            'core': self._config_to_dict(self.core),
            'llm': self._config_to_dict(self.llm),
            'dify': self._config_to_dict(self.dify),
            'openclaw': self._config_to_dict(self.openclaw),
            'security': self._config_to_dict(self.security),
            'device': self._config_to_dict(self.device)
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

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