"""AgencyOS Web服务器主入口"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core.runtime import AgentRuntime
from src.web.api import setup_app

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def start_server(host: str = "0.0.0.0", port: int = 18789):
    """启动Web服务器"""
    logger.info(f"Starting AgencyOS server on {host}:{port}")
    
    # 创建运行时实例
    runtime = AgentRuntime()
    await runtime.initialize()
    
    # 设置Web应用
    app = setup_app(runtime)
    
    # 创建TCP服务器
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info(f"Server started successfully on {host}:{port}")
    logger.info("API endpoints available:")
    logger.info(f"  Health check: http://{host}:{port}/api/health")
    logger.info(f"  List characters: http://{host}:{port}/api/user/{{user_id}}/characters")
    logger.info(f"  Get character: http://{host}:{port}/api/character/{{character_id}}")
    
    try:
        # 保持服务器运行
        await asyncio.Future()  # 永远等待，直到被取消
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    from aiohttp import web
    
    parser = argparse.ArgumentParser(description="AgencyOS Web Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("-p", "--port", type=int, default=18789, help="Port to bind to")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(start_server(args.host, args.port))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)