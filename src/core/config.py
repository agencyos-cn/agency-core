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

    def get_character_specific_config(self, character_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """获取角色特定的配置"""
        if not character_config:
            return {
                "llm": self.llm,
                "dify": self.dify,
                "openclaw": self.openclaw,
                "core": self.core,
                "security": self.security,
                "device": self.device
            }
        
        # 合并全局配置和角色特定配置
        result = {
            "llm": self.llm,
            "dify": self.dify,
            "openclaw": self.openclaw,
            "core": self.core,
            "security": self.security,
            "device": self.device
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
                host=char_core_config.get("host", self.core.host),
                port=char_core_config.get("port", self.core.port),
                debug=char_core_config.get("debug", self.core.debug),
                log_level=char_core_config.get("log_level", self.core.log_level),
                cors_origins=char_core_config.get("cors_origins", self.core.cors_origins),
                enable_third_party_ecosystem=char_core_config.get("enable_third_party_ecosystem", self.core.enable_third_party_ecosystem),
                ecosystem_mode=char_core_config.get("ecosystem_mode", self.core.ecosystem_mode),
                plugin_directory=char_core_config.get("plugin_directory", self.core.plugin_directory),
                cache_backend=char_core_config.get("cache_backend", self.core.cache_backend),
                cache_ttl=char_core_config.get("cache_ttl", self.core.cache_ttl)
            )
            
        # 如果角色有特定的安全配置，覆盖全局配置
        if "security" in character_config:
            char_security_config = character_config["security"]
            result["security"] = SecurityConfig(
                jwt_secret_key=char_security_config.get("jwt_secret_key", self.security.jwt_secret_key),
                jwt_algorithm=char_security_config.get("jwt_algorithm", self.security.jwt_algorithm),
                access_token_expire_minutes=char_security_config.get("access_token_expire_minutes", self.security.access_token_expire_minutes),
                refresh_token_expire_days=char_security_config.get("refresh_token_expire_days", self.security.refresh_token_expire_days),
                rate_limit_per_minute=char_security_config.get("rate_limit_per_minute", self.security.rate_limit_per_minute),
                enable_csp=char_security_config.get("enable_csp", self.security.enable_csp),
                csp_policy=char_security_config.get("csp_policy", self.security.csp_policy),
                allowed_hosts=char_security_config.get("allowed_hosts", self.security.allowed_hosts),
                enable_https_redirect=char_security_config.get("enable_https_redirect", self.security.enable_https_redirect),
                enable_hsts=char_security_config.get("enable_hsts", self.security.enable_hsts),
                secure_cookies=char_security_config.get("secure_cookies", self.security.secure_cookies),
                csrf_protect=char_security_config.get("csrf_protect", self.security.csrf_protect)
            )
            
        # 如果角色有特定的设备配置，覆盖全局配置
        if "device" in character_config:
            char_device_config = character_config["device"]
            result["device"] = DeviceConfig(
                device_type=char_device_config.get("device_type", self.device.device_type),
                device_name=char_device_config.get("device_name", self.device.device_name),
                manufacturer=char_device_config.get("manufacturer", self.device.manufacturer),
                model=char_device_config.get("model", self.device.model),
                os=char_device_config.get("os", self.device.os),
                os_version=char_device_config.get("os_version", self.device.os_version),
                capabilities=char_device_config.get("capabilities", self.device.capabilities),
                supported_features=char_device_config.get("supported_features", self.device.supported_features),
                permissions=char_device_config.get("permissions", self.device.permissions),
                location_services_enabled=char_device_config.get("location_services_enabled", self.device.location_services_enabled),
                battery_saving_mode=char_device_config.get("battery_saving_mode", self.device.battery_saving_mode),
                network_status=char_device_config.get("network_status", self.device.network_status),
                connection_type=char_device_config.get("connection_type", self.device.connection_type),
                signal_strength=char_device_config.get("signal_strength", self.device.signal_strength),
                storage_capacity=char_device_config.get("storage_capacity", self.device.storage_capacity),
                available_storage=char_device_config.get("available_storage", self.device.available_storage),
                memory_capacity=char_device_config.get("memory_capacity", self.device.memory_capacity),
                available_memory=char_device_config.get("available_memory", self.device.available_memory)
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

    def save_to_file(self, config_file: str):
        """保存配置到文件"""
        config_data = {
            "core": self.core.__dict__,
            "llm": self.llm.__dict__,
            "dify": self.dify.__dict__,
            "openclaw": self.openclaw.__dict__,
            "security": self.security.__dict__,
            "device": self.device.__dict__
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