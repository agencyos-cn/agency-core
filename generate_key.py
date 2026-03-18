#!/usr/bin/env python3
"""
密钥生成工具
用于生成安全的JWT加密密钥
"""

import secrets
import argparse


def generate_key(length: int = 32) -> str:
    """
    生成安全的随机密钥
    
    Args:
        length: 密钥长度（字节），默认32字节(256位)
        
    Returns:
        URL安全的随机字符串
    """
    return secrets.token_urlsafe(length)


def main():
    parser = argparse.ArgumentParser(description='生成安全的JWT加密密钥')
    parser.add_argument('-l', '--length', type=int, default=32,
                        help='密钥长度（字节），默认32字节(256位)')
    parser.add_argument('--count', type=int, default=1,
                        help='生成密钥的数量，默认1个')
    
    args = parser.parse_args()
    
    print(f"生成 {args.count} 个长度为 {args.length} 字节的密钥：\n")
    
    for i in range(args.count):
        key = generate_key(args.length)
        print(f"密钥 {i+1}: {key}")
    
    print(f"\n提示：将生成的密钥添加到 .env 文件中的 ENCRYPTION_KEY 变量")


if __name__ == "__main__":
    main()