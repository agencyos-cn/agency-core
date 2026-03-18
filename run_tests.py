#!/usr/bin/env python3
"""运行所有测试的脚本"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """运行测试"""
    print("Running AgencyOS tests...")
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 确保当前目录在Python路径中
    sys.path.insert(0, str(project_root))
    
    # 运行pytest
    try:
        # 首先检查pytest是否已安装
        import pytest
    except ImportError:
        print("pytest not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"])
        import pytest
    
    # 运行测试
    exit_code = pytest.main([
        "tests/",
        "-v",                    # 详细输出
        "--tb=short",            # 简短的traceback
        "-x",                    # 遇到失败立即停止
        "--asyncio-mode=auto"    # asyncio模式
    ])
    
    return exit_code


def run_unit_tests_only():
    """仅运行单元测试"""
    print("Running unit tests only...")
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    sys.path.insert(0, str(project_root))
    
    try:
        import pytest
    except ImportError:
        print("pytest not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"])
        import pytest
    
    # 运行测试，排除集成测试
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--tb=short",
        "-k", "not integration",  # 跳过标记为集成测试的测试
        "--asyncio-mode=auto"
    ])
    
    return exit_code


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "unit":
        exit_code = run_unit_tests_only()
    else:
        exit_code = run_tests()
    
    print(f"\nTests completed with exit code: {exit_code}")
    sys.exit(exit_code)