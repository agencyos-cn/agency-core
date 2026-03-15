"""Logging Utility"""

import logging
import sys
from datetime import datetime


class Logger:
    """日志记录器，提供统一的日志记录功能"""
    
    def __init__(self, name="AgencyOS", level=logging.INFO):
        """初始化日志记录器
        
        Args:
            name (str): 记录器名称
            level (int): 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def debug(self, message):
        """记录调试信息
        
        Args:
            message (str): 调试消息
        """
        self.logger.debug(message)
    
    def info(self, message):
        """记录普通信息
        
        Args:
            message (str): 普通消息
        """
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告信息
        
        Args:
            message (str): 警告消息
        """
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误信息
        
        Args:
            message (str): 错误消息
        """
        self.logger.error(message)
    
    def critical(self, message):
        """记录严重错误信息
        
        Args:
            message (str): 严重错误消息
        """
        self.logger.critical(message)


def get_logger(name="AgencyOS", level=logging.INFO):
    """获取日志记录器实例
    
    Args:
        name (str): 记录器名称
        level (int): 日志级别
        
    Returns:
        Logger: 日志记录器实例
    """
    return Logger(name, level)