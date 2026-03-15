"""BaseSkill - 所有技能的基类"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseSkill(ABC):
    """所有技能的抽象基类"""
    
    def __init__(self, skill_id: Optional[str] = None, 
                 name: Optional[str] = None, 
                 version: Optional[str] = "0.1.0"):
        # 如果没传参数，尝试从类属性获取
        self.skill_id = skill_id or getattr(self.__class__, "skill_id", self.__class__.__name__.lower())
        self.name = name or getattr(self.__class__, "name", self.__class__.__name__)
        self.version = version or getattr(self.__class__, "version", "0.1.0")
        
        self.config = {}
        logger.debug("Skill %s (%s) initialized", self.name, self.skill_id)
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any], context) -> Dict[str, Any]:
        """执行技能的核心方法
        
        Args:
            params: 技能参数
            context: 执行上下文
        
        Returns:
            执行结果
        """
        pass
    
    async def validate(self, params: Dict[str, Any]) -> bool:
        """验证参数是否合法
        
        Args:
            params: 待验证的参数
        
        Returns:
            参数是否合法
        """
        return True
    
    async def initialize(self, config: Optional[Dict] = None):
        """初始化技能（可选）"""
        if config:
            self.config.update(config)
        logger.info("Skill %s initialized", self.name)
    
    async def shutdown(self):
        """关闭技能，释放资源（可选）"""
        logger.info("Skill %s shutdown", self.name)