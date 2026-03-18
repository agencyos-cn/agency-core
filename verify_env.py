#!/usr/bin/env python3
"""
环境变量验证脚本
用于验证 .env 文件中的配置是否正确加载
"""

import os
from src.core.security_config import SecurityConfig


def verify_environment():
    """验证环境变量配置"""
    print("验证环境变量配置...")
    
    # 创建安全配置实例
    config = SecurityConfig()
    
    print(f"加密功能启用: {config.encryption_enabled}")
    print(f"加密密钥长度: {len(config.encryption_key)} 字符")
    print(f"加密密钥前20字符: {config.encryption_key[:20]}...")
    
    # 检查是否使用了默认密钥（开发用）
    default_key_part = "your-super-secret-jwt-signing-key"
    if default_key_part in config.encryption_key:
        print("\n⚠️  警告: 检测到默认密钥，这在生产环境中不安全!")
        print("请确保在 .env 文件中设置了 ENCRYPTION_KEY 环境变量")
    else:
        print("\n✅ 加密密钥已从环境变量正确加载")
        
    # 验证密钥长度
    if len(config.encryption_key) >= 32:
        print("✅ 密钥长度满足安全要求（≥32字符）")
    else:
        print("❌ 密钥长度不足，建议使用至少32字符的密钥")
    
    # 显示其他重要环境变量
    print("\n其他环境变量:")
    server_host = os.getenv("SERVER_HOST", "未设置")
    server_port = os.getenv("SERVER_PORT", "未设置")
    print(f"  SERVER_HOST: {server_host}")
    print(f"  SERVER_PORT: {server_port}")


if __name__ == "__main__":
    verify_environment()