"""DeviceController - 设备控制技能"""

import logging
from typing import Dict, Any

from src.skills.base import BaseSkill

logger = logging.getLogger(__name__)

class DeviceController(BaseSkill):
    """设备控制技能
    处理开关灯、空调等设备控制指令
    """
    
    skill_id = "device_controller"
    name = "设备控制器"
    version = "0.1.0"
    
    def __init__(self):
        super().__init__()  # 使用新的基类初始化，自动从类属性读取
        self.supported_devices = ["light", "air_conditioner", "tv"]
    
    async def execute(self, params: Dict[str, Any], context) -> Dict[str, Any]:
        """执行设备控制
        
        Args:
            params: 包含设备类型和动作的参数
            context: 执行上下文
        """
        logger.info(f"Executing device control: {params}")
        
        # 从参数中提取信息
        intent_text = params.get('intent', '')
        
        # 简单的规则解析
        if '开灯' in intent_text:
            return {
                "success": True,
                "message": "已为您打开灯光",
                "device": "light",
                "action": "turn_on"
            }
        elif '关灯' in intent_text:
            return {
                "success": True,
                "message": "已为您关闭灯光",
                "device": "light",
                "action": "turn_off"
            }
        elif '开空调' in intent_text:
            return {
                "success": True,
                "message": "已为您打开空调",
                "device": "air_conditioner",
                "action": "turn_on"
            }
        else:
            return {
                "success": False,
                "message": f"暂不支持控制: {intent_text}"
            }