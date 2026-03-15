"""Base Skill Class Definition"""

class BaseSkill:
    """技能基类，所有具体技能需要继承此类"""
    
    def __init__(self, name, description=""):
        """初始化技能
        
        Args:
            name (str): 技能名称
            description (str): 技能描述
        """
        self.name = name
        self.description = description
    
    def execute(self, *args, **kwargs):
        """执行技能逻辑，子类需要实现此方法
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    def validate_inputs(self, *args, **kwargs):
        """验证输入参数
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            bool: 验证是否通过
        """
        return True