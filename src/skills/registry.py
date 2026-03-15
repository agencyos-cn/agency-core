"""SkillRegistry - 技能注册表"""

import logging
from typing import Dict, Optional, Type
from .base import BaseSkill

logger = logging.getLogger(__name__)

class SkillRegistry:
    """技能注册表
    管理所有可用的技能类，支持按 ID、名称查找
    """
    
    def __init__(self):
        self._skills_by_id: Dict[str, Type[BaseSkill]] = {}
        self._skills_by_name: Dict[str, str] = {}  # name -> id
        logger.debug("SkillRegistry initialized")
    
    def register(self, skill_class: Type[BaseSkill], skill_id: Optional[str] = None):
        """注册一个技能类
        
        Args:
            skill_class: 技能类（必须是 BaseSkill 的子类）
            skill_id: 技能 ID，如果不提供则使用 skill_class.skill_id
        """
        if not issubclass(skill_class, BaseSkill):
            raise TypeError(f"{skill_class.__name__} must inherit from BaseSkill")
        
        # 获取技能 ID
        skill_id = skill_id or getattr(skill_class, "skill_id", None)
        if not skill_id:
            skill_id = skill_class.__name__.lower()
        
        # 获取技能名称
        skill_name = getattr(skill_class, "name", skill_class.__name__)
        
        if skill_id in self._skills_by_id:
            logger.warning("Skill ID %s already registered, overwriting", skill_id)
        
        self._skills_by_id[skill_id] = skill_class
        self._skills_by_name[skill_name] = skill_id
        logger.info("Registered skill: %s (ID: %s)", skill_name, skill_id)
    
    def get(self, skill_id: str) -> Optional[Type[BaseSkill]]:
        """根据技能 ID 获取技能类"""
        return self._skills_by_id.get(skill_id)
    
    def get_by_name(self, name: str) -> Optional[Type[BaseSkill]]:
        """根据技能名称获取技能类"""
        skill_id = self._skills_by_name.get(name)
        if skill_id:
            return self.get(skill_id)
        return None
    
    def list_skills(self) -> Dict[str, str]:
        """列出所有已注册的技能"""
        return {
            name: skill_id
            for name, skill_id in self._skills_by_name.items()
        }
    
    def create_instance(self, skill_id: str, **kwargs) -> Optional[BaseSkill]:
        """创建技能实例
        
        Args:
            skill_id: 技能 ID
            **kwargs: 传递给技能构造函数的参数
        
        Returns:
            技能实例，如果技能未注册则返回 None
        """
        skill_class = self.get(skill_id)
        if not skill_class:
            logger.warning("Skill %s not found", skill_id)
            return None
        
        return skill_class(**kwargs)