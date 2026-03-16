#!/usr/bin/env python3
"""
安装测试所需的依赖包
"""

import subprocess
import sys
import importlib

def install_if_missing(package_name, import_name=None):
    """
    检查并安装缺失的包
    """
    if import_name is None:
        import_name = package_name
        
    try:
        importlib.import_module(import_name)
        print(f"✓ {package_name} 已安装")
    except ImportError:
        print(f"- 正在安装 {package_name} ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✓ {package_name} 安装成功")
        except subprocess.CalledProcessError:
            print(f"✗ {package_name} 安装失败")
            return False
    return True

def main():
    print("正在检查测试所需的依赖包...")
    
    # 检查测试脚本所需的包
    packages_to_check = [
        ("websockets", "websockets"),
    ]
    
    all_installed = True
    for pkg, import_name in packages_to_check:
        if not install_if_missing(pkg, import_name):
            all_installed = False
    
    if all_installed:
        print("\n所有依赖包均已安装完成！")
    else:
        print("\n部分依赖包安装失败，请手动安装后重试。")
        sys.exit(1)

if __name__ == "__main__":
    main()