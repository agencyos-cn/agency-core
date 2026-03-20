"""
Test script to verify the version endpoint works correctly
"""
import aiohttp
import asyncio
from src.version import __version__

async def test_version_endpoint():
    """Test the version endpoint"""
    try:
        # Assuming the server is running on default port
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:18789/api/version') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"API Version: {data['version']}")
                    print(f"Service: {data['service']}")
                    print(f"Timestamp: {data['timestamp']}")
                    print(f"Matches source: {data['version'] == __version__}")
                else:
                    print(f"Request failed with status {response.status}")
                    # Server可能未运行，这是正常的
                    print("Note: This might fail if the server is not running.")
                    
    except aiohttp.client_exceptions.ClientConnectorError:
        print("Could not connect to server. Make sure agency-core backend is running on port 18789.")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    print(f"Expected backend version: {__version__}")
    asyncio.run(test_version_endpoint())