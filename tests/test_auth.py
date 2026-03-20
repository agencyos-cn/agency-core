"""
测试用户认证功能的脚本
"""
import asyncio
import aiohttp
import json


async def test_auth():
    base_url = "http://localhost:18789"
    
    async with aiohttp.ClientSession() as session:
        print("开始测试用户认证功能...")
        
        # 1. 测试注册功能
        print("\n1. 测试用户注册...")
        register_data = {
            "name": "测试用户",
            "email": "test@example.com",
            "password": "password123"
        }
        
        async with session.post(f"{base_url}/api/auth/register", json=register_data) as resp:
            print(f"注册响应: {resp.status}")
            response_text = await resp.text()
            print(f"响应内容: {response_text}")
            
            if resp.status == 200:
                print("✓ 用户注册成功")
            elif resp.status == 400:
                print("⚠ 用户可能已存在或输入有误")
            else:
                print(f"✗ 注册失败，状态码: {resp.status}")
        
        # 2. 测试登录功能
        print("\n2. 测试用户登录...")
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        async with session.post(f"{base_url}/api/auth/login", json=login_data) as resp:
            print(f"登录响应: {resp.status}")
            response_text = await resp.text()
            print(f"响应内容: {response_text}")
            
            if resp.status == 200:
                response_json = json.loads(response_text)
                token = response_json.get('token')
                if token:
                    print("✓ 用户登录成功")
                    print(f"获取到令牌: {token[:20]}...")  # 只显示令牌的前20个字符
                else:
                    print("✗ 登录响应中未包含令牌")
            else:
                print(f"✗ 登录失败，状态码: {resp.status}")
        
        # 3. 测试获取用户信息功能
        print("\n3. 测试获取用户信息...")
        headers = {
            "Authorization": f"Bearer {token if 'token' in locals() else 'invalid_token'}"
        }
        
        async with session.get(f"{base_url}/api/auth/me", headers=headers) as resp:
            print(f"获取用户信息响应: {resp.status}")
            response_text = await resp.text()
            print(f"响应内容: {response_text}")
            
            if resp.status == 200:
                print("✓ 获取用户信息成功")
            else:
                print(f"✗ 获取用户信息失败，状态码: {resp.status}")
        
        print("\n测试完成!")


if __name__ == "__main__":
    print("注意：请先启动后端服务再运行此测试脚本")
    print("启动后端服务命令: python main.py")
    
    try:
        asyncio.run(test_auth())
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        print("请确保后端服务正在运行")