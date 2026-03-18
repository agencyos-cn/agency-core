"""大模型配置"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class LLMConfig:
    """大模型配置项"""
    # 本地模型配置（备用）
    local_model_enabled: bool = False          # 是否启用本地模型
    local_model_provider: str = "ollama"       # 本地模型提供商 (ollama, vllm, etc.)
    local_model_name: str = "llama2"           # 本地模型名称
    local_api_base: str = "http://localhost:11434/v1"  # 本地API地址
    local_api_key: str = "local-key"           # 本地API密钥
    
    # 第三方模型提供商配置
    providers: Optional[Dict[str, Any]] = None  # 各提供商配置
    default_provider: str = "openai"           # 默认提供商
    fallback_providers: Optional[List[str]] = None  # 降级提供商列表
    
    # 模型选择策略
    enable_model_fallback: bool = True         # 启用模型降级
    request_timeout: int = 30                  # 请求超时时间
    max_retries: int = 3                      # 最大重试次数
    
    # 第三方生态集成
    third_party_models_enabled: bool = True    # 是否启用第三方模型
    integrated_platforms: Optional[List[str]] = None  # 已集成的平台列表
    model_marketplace_urls: Optional[Dict[str, str]] = None  # 模型市场URL映射


# 默认配置
DEFAULT_LLM_CONFIG = LLMConfig(
    local_model_enabled=False,
    local_model_provider="ollama",
    local_model_name="llama2",
    local_api_base="http://localhost:11434/v1",
    local_api_key="local-key",
    providers={},
    default_provider="openai",
    fallback_providers=["anthropic", "google"],
    integrated_platforms=[
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
    model_marketplace_urls={
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
)