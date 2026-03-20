import asyncio
import aiohttp
import json

async def test_api():
    url = "http://localhost:18789"
    
    # 测试健康检查
    async with aiohttp.ClientSession() as session:
        try:
            print("Testing health check...")
            async with session.get(f"{url}/api/health") as resp:
                print(f"Health check response: {resp.status}")
                print(await resp.text())
        except Exception as e:
            print(f"Health check error: {e}")
        
        print("\nTesting register endpoint...")
        try:
            register_data = {
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123"
            }
            async with session.post(f"{url}/api/auth/register", json=register_data) as resp:
                print(f"Register response: {resp.status}")
                print(await resp.text())
        except Exception as e:
            print(f"Register error: {e}")

if __name__ == "__main__":
    print("Waiting for server to start...")
    asyncio.run(test_api())