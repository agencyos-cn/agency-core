#!/usr/bin/env python
"""创建初始用户的脚本"""

import sys
import os
from src.core.auth.user_manager import UserManager

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath('.'))

def create_initial_user():
    print("创建初始用户...")
    
    # 获取用户输入
    name = input("请输入用户名: ").strip()
    email = input("请输入邮箱: ").strip()
    password = input("请输入密码: ").strip()
    
    if not name or not email or not password:
        print("❌ 错误: 所有字段都是必填项")
        return False
    
    try:
        user_manager = UserManager()
        user = user_manager.create_user(name, email, password)
        
        if user:
            print(f"✅ 用户 {email} 创建成功!")
            print(f"用户ID: {user.id}")
            print(f"用户名: {user.name}")
            print(f"邮箱: {user.email}")
            print(f"角色: {user.role}")
            return True
        else:
            print(f"❌ 用户 {email} 创建失败 - 邮箱可能已被注册")
            return False
    except Exception as e:
        print(f"❌ 创建用户时出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_initial_user()
    if success:
        print("\n🎉 初始用户创建成功！现在您应该可以使用这些凭据登录了。")
    else:
        print("\n❌ 初始用户创建失败。")