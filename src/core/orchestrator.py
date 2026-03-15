"""SkillOrchestrator - 技能编排器"""

import logging
from typing import Dict, Any, Optional, List
import importlib
import pkgutil
from pathlib import Path

logger = logging.getLogger(__name__)

class SkillOrchestrator:
    """技能编排器
    负责发现、加载和调用技能，并编排多技能协作
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.skills = {}  # skill_name -> skill_instance
        self.skill_paths = self.config.get("paths", ["skills"])
        logger.info("SkillOrchestrator initialized with paths: %s", self.skill_paths)
    
    async def initialize(self):
        """初始化技能编排器，发现并加载技能"""
        logger.info("Initializing SkillOrchestrator...")
        
        # 发现技能
        await self._discover_skills()
        
        logger.info("SkillOrchestrator initialized with %d skills", len(self.skills))
    
    async def _discover_skills(self):
        """发现可用的技能"""
        logger.info("Discovering skills...")
        
        # 导入并注册技能
        try:
            from src.skills import DeviceController, QueryHandler
            
            # 创建技能实例
            self.skills["device_controller"] = DeviceController()
            self.skills["query_handler"] = QueryHandler()
            
            logger.info("Discovered skills: %s", list(self.skills.keys()))
        except ImportError as e:
            logger.error(f"Failed to import skills: {e}")
    
    async def create_plan(self, intent: Dict[str, Any], context) -> Dict[str, Any]:
        """根据意图创建执行计划
        
        Args:
            intent: 意图理解引擎输出的结构化意图
            context: 运行时上下文
        
        Returns:
            执行计划
        """
        logger.debug("Creating plan for intent: %s", intent)
        
        # TODO: 根据意图选择合适的技能
        intent_type = intent.get("type", "unknown")
        
        if intent_type == "device_control":
            # 设备控制意图，可能需要调用多个技能
            plan = {
                "steps": [
                    {
                        "skill": "device_controller",
                        "params": intent
                    }
                ],
                "response": "正在处理设备控制请求"
            }
        elif intent_type == "query":
            plan = {
                "steps": [
                    {
                        "skill": "query_handler",
                        "params": intent
                    }
                ],
                "response": "正在查询..."
            }
        else:
            plan = {
                "steps": [],
                "response": "抱歉，我还不能理解这个请求"
            }
        
        return plan
    
    async def execute_skill(self, skill_name: str, params: Dict, context) -> Any:
        """执行单个技能"""
        if skill_name not in self.skills:
            logger.warning("Skill %s not found", skill_name)
            return {"error": f"Skill {skill_name} not found"}
        
        skill = self.skills[skill_name]
        logger.debug("Executing skill %s with params: %s", skill_name, params)
        
        return await skill.execute(params, context)
    
    async def shutdown(self):
        """关闭编排器"""
        logger.info("Shutting down SkillOrchestrator...")
        for skill in self.skills.values():
            if hasattr(skill, "shutdown"):
                await skill.shutdown()
        logger.info("SkillOrchestrator shutdown complete")


class EchoSkill:
    """简单的回显技能，用于测试"""
    
    async def execute(self, params: Dict, context) -> Dict:
        return {
            "message": f"Echo: {params.get('intent', 'hello')}",
            "success": True
        }
    
    async def shutdown(self):
        pass