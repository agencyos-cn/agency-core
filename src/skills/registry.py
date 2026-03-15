"""Skill Registry"""

class SkillRegistry:
    """技能注册表，用于统一管理和查找所有可用技能"""
    
    def __init__(self):
        """初始化注册表"""
        self._skills = {}
    
    def register(self, skill_class):
        """注册技能类到注册表
        
        Args:
            skill_class: 技能类
        """
        skill_name = skill_class.__name__
        self._skills[skill_name] = skill_class
        return skill_class
    
    def get_skill(self, skill_name):
        """获取注册的技能类
        
        Args:
            skill_name (str): 技能名称
            
        Returns:
            技能类或者None（如果找不到）
        """
        return self._skills.get(skill_name)
    
    def list_skills(self):
        """列出所有注册的技能
        
        Returns:
            list: 技能名称列表
        """
        return list(self._skills.keys())
    
    def has_skill(self, skill_name):
        """检查技能是否已注册
        
        Args:
            skill_name (str): 技能名称
            
        Returns:
            bool: 是否已注册
        """
        return skill_name in self._skills