"""OpenClaw服务配置"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class OpenClawConfig:
    """OpenClaw服务配置项"""
    # OpenClaw服务地址
    api_base: str = "http://localhost:8080/v1"  # OpenClaw API基础地址
    api_key: str = ""                           # OpenClaw API密钥
    app_id: str = ""                            # OpenClaw应用ID
    
    # 第三方模型提供商配置
    third_party_llm_providers: Optional[Dict[str, Any]] = None  # 第三方LLM提供商配置
    enable_remote_models: bool = True           # 是否启用远程模型
    
    # 第三方技能配置
    external_skill_sources: Optional[list] = None  # 外部技能来源列表
    sync_external_skills: bool = True           # 是否同步外部技能
    skill_sync_interval: int = 3600            # 技能同步间隔（秒）
    
    # 渠道配置
    channels: Optional[Dict[str, Any]] = None   # 支持的IM渠道配置
    enable_multi_channel: bool = True          # 是否启用多渠道
    
    # 模型和技能缓存
    model_cache_ttl: int = 3600                # 模型信息缓存时间
    skill_cache_ttl: int = 1800                # 技能信息缓存时间


# 默认配置
DEFAULT_OPENCLAW_CONFIG = OpenClawConfig(
    api_base="http://localhost:8080/v1",
    api_key="",
    app_id="",
    third_party_llm_providers={},
    external_skill_sources=[],
    channels={},
)