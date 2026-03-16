"""本地 WebSocket 测试服务器"""

import asyncio
import logging

try:
    import websockets
except ImportError:
    print("错误: 缺少 websockets 依赖包，请运行以下命令安装:")
    print("pip install websockets")
    exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def echo_handler(websocket):
    """回显处理器"""
    async for message in websocket:
        logger.info(f"Received: {message}")
        await websocket.send(message)
        logger.info(f"Echoed: {message}")

async def main():
    """启动 WebSocket 服务器"""
    async with websockets.serve(echo_handler, "localhost", 8765):
        logger.info("WebSocket test server running on ws://localhost:8765")
        await asyncio.Future()  # 运行 forever

if __name__ == "__main__":
    asyncio.run(main())