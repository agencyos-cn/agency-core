"""Skill Orchestrator"""

class Orchestrator:
    """技能编排器，负责协调和执行多个技能"""
    
    def __init__(self):
        """初始化编排器"""
        self.skills = {}
    
    def register_skill(self, skill_name, skill_instance):
        """注册技能到编排器
        
        Args:
            skill_name (str): 技能名称
            skill_instance: 技能实例
        """
        self.skills[skill_name] = skill_instance
    
    def execute_skill(self, skill_name, *args, **kwargs):
        """执行指定技能
        
        Args:
            skill_name (str): 要执行的技能名称
            *args: 传递给技能的位置参数
            **kwargs: 传递给技能的关键字参数
            
        Returns:
            技能执行结果
        """
        if skill_name in self.skills:
            return self.skills[skill_name].execute(*args, **kwargs)
        else:
            raise ValueError(f"Skill {skill_name} not found")