#!/usr/bin/env python
"""用于调试认证系统的测试脚本"""

import sys
import os
import asyncio
import pymysql
from src.core.auth.user_manager import UserManager
from src.core.database.models import User

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath('.'))

def test_database_connection():
    """测试数据库连接"""
    print("正在测试数据库连接...")
    try:
        user_manager = UserManager()
        print("✅ 数据库连接成功!")
        print(f"数据库配置: host={user_manager.connection_params['host']}, "
              f"database={user_manager.connection_params['database']}")
        return user_manager
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def test_user_exists(user_manager, email):
    """测试特定用户是否存在"""
    print(f"\n正在检查用户 {email} 是否存在...")
    try:
        user = user_manager.get_user_by_email(email)
        if user:
            print(f"✅ 用户 {email} 存在:")
            print(f"   ID: {user.id}")
            print(f"   姓名: {user.name}")
            print(f"   角色: {user.role}")
            return user
        else:
            print(f"❌ 用户 {email} 不存在")
            return None
    except Exception as e:
        print(f"❌ 检查用户时出错: {e}")
        return None

def test_password_verification(user_manager, email, password):
    """测试密码验证"""
    print(f"\n正在验证用户 {email} 的密码...")
    try:
        user = user_manager.authenticate_user(email, password)
        if user:
            print(f"✅ 密码验证成功!")
            return True
        else:
            print(f"❌ 密码验证失败!")
            return False
    except Exception as e:
        print(f"❌ 验证密码时出错: {e}")
        return False

def create_test_user(user_manager, name, email, password):
    """创建测试用户"""
    print(f"\n正在创建测试用户 {email}...")
    try:
        user = user_manager.create_user(name, email, password)
        if user:
            print(f"✅ 用户 {email} 创建成功!")
            return user
        else:
            print(f"❌ 用户 {email} 创建失败 - 可能邮箱已存在")
            return None
    except Exception as e:
        print(f"❌ 创建用户时出错: {e}")
        return None

def list_all_users(user_manager):
    """列出所有用户"""
    print("\n正在列出所有用户...")
    try:
        conn = pymysql.connect(**user_manager.connection_params)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, email, role, created_at FROM users")
        rows = cursor.fetchall()
        
        if rows:
            print("📋 所有用户:")
            for row in rows:
                print(f"   ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Role: {row[3]}, Created: {row[4]}")
        else:
            print("   没有找到任何用户")
        
        conn.close()
    except Exception as e:
        print(f"❌ 列出用户时出错: {e}")

async def main():
    print("="*50)
    print("认证系统调试工具")
    print("="*50)
    
    # 测试数据库连接
    user_manager = test_database_connection()
    if not user_manager:
        return
    
    # 列出所有现有用户
    list_all_users(user_manager)
    
    # 测试特定的用户认证
    print("\n" + "="*50)
    print("请输入要测试的用户凭据:")
    email = input("邮箱: ").strip() or "test@example.com"
    password = input("密码: ").strip() or "password123"
    
    # 检查用户是否存在
    user = test_user_exists(user_manager, email)
    
    if not user:
        print(f"\n用户 {email} 不存在，是否创建一个测试用户？(y/n): ", end="")
        response = input().strip().lower()
        if response == 'y':
            name = input("请输入用户名: ").strip() or "Test User"
            user = create_test_user(user_manager, name, email, password)
            if user:
                print(f"✅ 测试用户 {email} 已创建，请重新尝试登录")
                return
    
    # 测试密码验证
    success = test_password_verification(user_manager, email, password)
    
    if success:
        print(f"\n🎉 登录测试成功！您可以使用邮箱 {email} 和提供的密码登录。")
    else:
        print(f"\n🔒 登录测试失败！请检查您的邮箱和密码。")

if __name__ == "__main__":
    asyncio.run(main())