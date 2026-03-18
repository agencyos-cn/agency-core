"""技能编排器 - 协调和执行各种技能"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from .runtime import RuntimeContext
from ..skills import SkillRegistry, Skill
from .character import CharacterManager

logger = logging.getLogger(__name__)


class SkillOrchestrator:
    """技能编排器，负责技能的调度和执行"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.skill_registry = SkillRegistry()
        self.character_manager = CharacterManager()
        self._initialized = False
        
        logger.info("SkillOrchestrator initialized with config: %s", self.config)
    
    async def initialize(self):
        """初始化技能编排器"""
        if self._initialized:
            return
            
        logger.info("Initializing SkillOrchestrator...")
        
        # 注册内置技能
        self._register_builtin_skills()
        
        self._initialized = True
        logger.info("SkillOrchestrator initialization completed")
    
    def _register_builtin_skills(self):
        """注册内置技能"""
        # 这里可以注册一些基础技能
        logger.debug("Registered builtin skills")
    
    async def create_plan(self, intent: Dict[str, Any], context: RuntimeContext) -> Dict[str, Any]:
        """根据意图创建执行计划
        
        Args:
            intent: 解析后的意图
            context: 运行时上下文
        
        Returns:
            执行计划
        """
        logger.debug("Creating execution plan for intent: %s", intent)
        
        # 获取角色信息以确定可用技能
        character = None
        if context.character_id:
            character = self.character_manager.get_character(context.character_id)
        else:
            # 如果没有指定角色，则使用默认角色
            character = self.character_manager.get_default_character(context.user_id)
        
        # 根据意图类型创建计划
        intent_type = intent.get("type", "unknown")
        
        # 检查角色权限
        allowed_skills = []
        if character:
            allowed_skills = character.allowed_skills or []
            # 如果角色有特定技能限制，则只允许这些技能
            if allowed_skills:
                available_skills = self._filter_allowed_skills(allowed_skills)
            else:
                available_skills = self.skill_registry.get_all_skills()
        else:
            available_skills = self.skill_registry.get_all_skills()
        
        # 根据意图类型生成计划
        if intent_type == "device_control":
            plan = await self._create_device_control_plan(intent, available_skills)
        elif intent_type == "query":
            plan = await self._create_query_plan(intent, available_skills)
        elif intent_type == "education_request":
            plan = await self._create_education_plan(intent, available_skills, character)
        elif intent_type == "legal_request":
            plan = await self._create_legal_plan(intent, available_skills, character)
        elif intent_type == "financial_request":
            plan = await self._create_financial_plan(intent, available_skills, character)
        elif intent_type == "dify_result":
            plan = await self._create_dify_plan(intent, available_skills)
        else:
            plan = await self._create_general_plan(intent, available_skills)
        
        # 如果角色有特定的回复长度要求，调整回复
        if character:
            plan = self._adjust_response_for_character(plan, character)
        
        return plan
    
    def _filter_allowed_skills(self, allowed_skills: List[str]) -> List[Skill]:
        """过滤出允许的技能"""
        all_skills = self.skill_registry.get_all_skills()
        return [skill for skill in all_skills if skill.name in allowed_skills]
    
    def _adjust_response_for_character(self, plan: Dict[str, Any], character) -> Dict[str, Any]:
        """根据角色调整回复"""
        response = plan.get("response", "")
        
        # 根据角色的沟通风格和语气偏好调整回复
        if character.communication_style == "casual":
            # 调整为更随意的语气
            response = response.replace("尊敬的用户", "朋友").replace("请注意", "记得")
        elif character.communication_style == "professional":
            # 调整为更专业的语气
            response = response.replace("朋友", "尊敬的用户").replace("记得", "请注意")
        
        # 根据回复长度偏好调整
        if character.response_length == "short":
            # 缩短回复
            sentences = response.split('。')
            if len(sentences) > 3:
                response = '。'.join(sentences[:3]) + "。"
        elif character.response_length == "long":
            # 扩展回复（如果AI模型支持）
            pass  # 在AI层面处理
        
        plan["response"] = response
        return plan
    
    async def _create_device_control_plan(self, intent: Dict[str, Any], available_skills: List[Skill]) -> Dict[str, Any]:
        """创建设备控制计划"""
        device = intent.get("device")
        action = intent.get("action")
        
        # 查找设备控制技能
        device_control_skill = next((skill for skill in available_skills 
                                   if skill.name == "device_control"), None)
        
        if device_control_skill:
            return {
                "response": f"正在为您{action}{device}...",
                "steps": [{
                    "skill": "device_control",
                    "params": {
                        "device": device,
                        "action": action
                    }
                }]
            }
        else:
            return {
                "response": f"抱歉，无法找到控制{device}的技能",
                "steps": []
            }
    
    async def _create_query_plan(self, intent: Dict[str, Any], available_skills: List[Skill]) -> Dict[str, Any]:
        """创建查询计划"""
        query_type = intent.get("query_type")
        
        return {
            "response": f"正在为您查询{query_type}信息...",
            "steps": [{
                "skill": "information_query",
                "params": {
                    "query_type": query_type
                }
            }]
        }
    
    async def _create_education_plan(self, intent: Dict[str, Any], available_skills: List[Skill], character) -> Dict[str, Any]:
        """创建教育计划"""
        subject_area = intent.get("subject_area", [])
        
        # 根据角色的专业领域调整回复
        if character and character.expertise_areas:
            subject_area = character.expertise_areas
            
        return {
            "response": f"作为您的教育导师，我将为您提供关于{'、'.join(subject_area)}方面的专业指导。",
            "steps": [{
                "skill": "education_assistance",
                "params": {
                    "subject_area": subject_area,
                    "personality_traits": getattr(character, 'personality_traits', []),
                    "communication_style": getattr(character, 'communication_style', 'professional')
                }
            }]
        }
    
    async def _create_legal_plan(self, intent: Dict[str, Any], available_skills: List[Skill], character) -> Dict[str, Any]:
        """创建法律计划"""
        legal_area = intent.get("legal_area", [])
        
        # 根据角色的专业领域调整回复
        if character and character.expertise_areas:
            legal_area = character.expertise_areas
            
        return {
            "response": f"作为您的法律顾问，我将为您提供关于{'、'.join(legal_area)}方面的专业建议。",
            "steps": [{
                "skill": "legal_assistance",
                "params": {
                    "legal_area": legal_area,
                    "personality_traits": getattr(character, 'personality_traits', []),
                    "communication_style": getattr(character, 'communication_style', 'professional')
                }
            }]
        }
    
    async def _create_financial_plan(self, intent: Dict[str, Any], available_skills: List[Skill], character) -> Dict[str, Any]:
        """创建金融计划"""
        finance_area = intent.get("finance_area", [])
        
        # 根据角色的专业领域调整回复
        if character and character.expertise_areas:
            finance_area = character.expertise_areas
            
        return {
            "response": f"作为您的金融顾问，我将为您提供关于{'、'.join(finance_area)}方面的专业意见。",
            "steps": [{
                "skill": "financial_advice",
                "params": {
                    "finance_area": finance_area,
                    "personality_traits": getattr(character, 'personality_traits', []),
                    "communication_style": getattr(character, 'communication_style', 'professional')
                }
            }]
        }
    
    async def _create_dify_plan(self, intent: Dict[str, Any], available_skills: List[Skill]) -> Dict[str, Any]:
        """创建Dify结果计划"""
        raw_response = intent.get("raw_response", {})
        answer = raw_response.get("answer", "抱歉，未能获取到相关信息。")
        
        return {
            "response": answer,
            "steps": []
        }
    
    async def _create_general_plan(self, intent: Dict[str, Any], available_skills: List[Skill]) -> Dict[str, Any]:
        """创建通用计划"""
        return {
            "response": "我已经收到您的请求，正在为您处理...",
            "steps": []
        }
    
    async def execute_skill(self, skill_name: str, params: Dict[str, Any], context: RuntimeContext) -> Dict[str, Any]:
        """执行指定技能
        
        Args:
            skill_name: 技能名称
            params: 技能参数
            context: 运行时上下文
        
        Returns:
            技能执行结果
        """
        logger.debug("Executing skill '%s' with params: %s", skill_name, params)
        
        # 获取角色信息以确定是否允许执行此技能
        character = None
        if context.character_id:
            character = self.character_manager.get_character(context.character_id)
        else:
            character = self.character_manager.get_default_character(context.user_id)
        
        # 检查角色权限
        if character and character.allowed_skills:
            if skill_name not in character.allowed_skills:
                return {
                    "status": "error",
                    "message": f"角色 '{character.name}' 没有权限执行技能 '{skill_name}'"
                }
        
        # 执行技能
        try:
            result = await self.skill_registry.execute(skill_name, params, context)
            logger.debug("Skill execution result: %s", result)
            return result
        except Exception as e:
            logger.error("Error executing skill '%s': %s", skill_name, str(e))
            return {
                "status": "error",
                "message": f"执行技能 '{skill_name}' 时发生错误: {str(e)}"
            }
    
    async def shutdown(self):
        """关闭技能编排器"""
        logger.info("Shutting down SkillOrchestrator...")
        # 清理资源
        logger.info("SkillOrchestrator shutdown complete")