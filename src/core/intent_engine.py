"""意图理解引擎"""

import logging
import re
from typing import Dict, Any, Optional, List
from .runtime import RuntimeContext
from .config import ConfigManager
from .character import CharacterManager, CharacterProfile

logger = logging.getLogger(__name__)


class IntentEngine:
    """意图理解引擎
    负责解析用户输入的自然语言，识别意图并提取参数
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.character_manager = CharacterManager()
        self.device_keywords = [
            "灯", "空调", "电视", "窗帘", "音响", "门锁", "插座", "风扇", "加湿器", "净化器"
        ]
        self.action_keywords = [
            "开", "关", "打开", "关闭", "启动", "停止", "调节", "设置", "播放", "暂停"
        ]
        self.query_keywords = [
            "天气", "新闻", "时间", "日期", "提醒", "日程", "邮件", "短信", "通话记录"
        ]
        
        logger.info("IntentEngine initialized")

    async def parse(self, user_input: str, context: RuntimeContext, character: Optional[CharacterProfile] = None) -> Dict[str, Any]:
        """解析用户输入，识别意图
        
        Args:
            user_input: 用户输入的自然语言
            context: 运行时上下文
            character: 使用的角色（如果指定）
        
        Returns:
            结构化的意图信息
        """
        logger.debug("Parsing user input: %s", user_input)
        
        # 1. 本地规则匹配（最快响应）
        local_intent = self._rule_based_parse(user_input, character)
        if local_intent['confidence'] >= 0.8:
            logger.info("Intent matched with high confidence using local rules: %s", local_intent)
            return local_intent
        
        # 2. 本地LLM解析（隐私保护、简单请求）
        if self.config_manager.llm.local_model_enabled:
            local_llm_intent = await self._local_llm_parse(user_input, context, character)
            if local_llm_intent['confidence'] > local_intent['confidence']:
                logger.info("Local LLM provided better intent: %s", local_llm_intent)
                return local_llm_intent
        
        # 3. Dify解析（复杂对话、工作流处理）
        if self.config_manager.dify.enable_remote_models and self.config_manager.dify.api_key:
            try:
                dify_intent = await self._dify_parse(user_input, context, character)
                logger.info("Received intent from Dify: %s", dify_intent)
                if dify_intent['confidence'] > local_intent['confidence']:
                    return dify_intent
            except Exception as e:
                logger.warning(f"Dify parsing failed: {e}")
        
        # 4. OpenClaw解析（多渠道接入、会话路由）
        if self.config_manager.openclaw.enable_remote_models and self.config_manager.openclaw.api_key:
            try:
                openclaw_intent = await self._openclaw_parse(user_input, context, character)
                logger.info("Received intent from OpenClaw: %s", openclaw_intent)
                if openclaw_intent['confidence'] > local_intent['confidence']:
                    return openclaw_intent
            except Exception as e:
                logger.warning(f"OpenClaw parsing failed: {e}")
        
        # 返回本地规则匹配的结果
        return local_intent

    def _rule_based_parse(self, user_input: str, character: Optional[CharacterProfile] = None) -> Dict[str, Any]:
        """基于规则的意图解析"""
        # 如果指定了角色，根据角色类型调整解析逻辑
        if character:
            # 教育角色
            if character.role_type.value == "teacher":
                education_keywords = ["学习", "课程", "考试", "作业", "知识", "教育", "教学"]
                if any(kw in user_input for kw in education_keywords):
                    return {
                        "type": "education_request",
                        "intent": user_input,
                        "subject_area": character.expertise_areas,
                        "confidence": 0.85,
                        "character_role": character.role_type.value,
                        "needs_cloud": True
                    }
            
            # 法律角色
            elif character.role_type.value == "lawyer":
                legal_keywords = ["法律", "案件", "诉讼", "合同", "纠纷", "权利", "义务", "法规"]
                if any(kw in user_input for kw in legal_keywords):
                    return {
                        "type": "legal_request",
                        "intent": user_input,
                        "legal_area": character.expertise_areas,
                        "confidence": 0.85,
                        "character_role": character.role_type.value,
                        "needs_cloud": True
                    }
            
            # 金融角色
            elif character.role_type.value == "financial_advisor":
                finance_keywords = ["投资", "理财", "股票", "基金", "财务", "收益", "风险", "资产"]
                if any(kw in user_input for kw in finance_keywords):
                    return {
                        "type": "financial_request",
                        "intent": user_input,
                        "finance_area": character.expertise_areas,
                        "confidence": 0.85,
                        "character_role": character.role_type.value,
                        "needs_cloud": True
                    }
        
        # 设备控制意图
        if any(keyword in user_input for keyword in self.device_keywords):
            # 检查是否包含动作关键词
            if any(action in user_input for action in self.action_keywords):
                device = self._extract_device(user_input)
                action = self._extract_action(user_input)
                
                return {
                    "type": "device_control",
                    "intent": user_input,
                    "device": device,
                    "action": action,
                    "confidence": 0.8,
                    "needs_cloud": False
                }
        
        # 查询意图
        if any(keyword in user_input for keyword in self.query_keywords):
            query_type = self._identify_query_type(user_input)
            return {
                "type": "query",
                "intent": user_input,
                "query_type": query_type,
                "confidence": 0.7,
                "needs_cloud": True
            }
        
        # 未知意图
        return {
            "type": "unknown",
            "intent": user_input,
            "confidence": 0.1,
            "needs_cloud": True  # 未知意图交由云端AI处理
        }

    def _extract_device(self, user_input: str) -> Optional[str]:
        """提取设备类型"""
        for keyword in self.device_keywords:
            if keyword in user_input:
                return keyword
        return None

    def _extract_action(self, user_input: str) -> Optional[str]:
        """提取动作"""
        for keyword in self.action_keywords:
            if keyword in user_input:
                return keyword
        return None

    def _identify_query_type(self, user_input: str) -> str:
        """识别查询类型"""
        for keyword in self.query_keywords:
            if keyword in user_input:
                return keyword
        return "general"

    async def _local_llm_parse(self, user_input: str, context: RuntimeContext, character: Optional[CharacterProfile] = None) -> Dict[str, Any]:
        """使用本地LLM解析意图"""
        # TODO: 实现本地LLM意图解析
        logger.debug("Using local LLM to parse intent: %s", user_input)
        # 如果有角色指定，可以在此处使用角色特定的配置
        return self._rule_based_parse(user_input, character)

    async def _dify_parse(self, user_input: str, context: RuntimeContext, character: Optional[CharacterProfile] = None) -> Dict[str, Any]:
        """使用Dify解析意图，支持角色特定配置"""
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {self.config_manager.dify.api_key}",
            "Content-Type": "application/json"
        }
        
        # 如果有角色配置，使用角色特定的Dify配置
        api_base = self.config_manager.dify.api_base
        if character and character.llm_config and 'dify' in character.llm_config:
            api_base = character.llm_config['dify'].get('api_base', api_base)
        
        data = {
            "inputs": {},
            "query": user_input,
            "response_mode": "blocking",
            "conversation_id": context.session_id,
            "user": context.user_id
        }
        
        # 如果有角色配置，添加角色相关信息
        if character:
            data["inputs"]["character_context"] = {
                "name": character.name,
                "role_type": character.role_type.value,
                "expertise": character.expertise_areas,
                "personality": character.personality_traits
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_base}/chat-messages", 
                json=data, 
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # 解析Dify返回的结果
                    intent_type = result.get("answer", "unknown")
                    confidence = 0.7  # 默认置信度
                    
                    # 根据Dify返回的信息提取意图
                    parsed_result = {
                        "type": "dify_result",  # 表示来自Dify的结果
                        "intent": intent_type,
                        "confidence": confidence,
                        "raw_response": result,
                        "needs_cloud": True
                    }
                    
                    if character:
                        parsed_result["character_role"] = character.role_type.value
                        
                    return parsed_result
                else:
                    logger.error(f"Dify API request failed with status {response.status}")
                    # 如果Dify解析失败，返回本地规则解析结果
                    return self._rule_based_parse(user_input, character)

    async def _openclaw_parse(self, user_input: str, context: RuntimeContext, character: Optional[CharacterProfile] = None) -> Dict[str, Any]:
        """使用OpenClaw解析意图，支持角色特定配置"""
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {self.config_manager.openclaw.api_key}",
            "Content-Type": "application/json"
        }
        
        # 如果有角色配置，使用角色特定的OpenClaw配置
        api_base = self.config_manager.openclaw.api_base
        if character and character.llm_config and 'openclaw' in character.llm_config:
            api_base = character.llm_config['openclaw'].get('api_base', api_base)
        
        data = {
            "input": user_input,
            "channel": "console",  # 默认控制台渠道
            "user_id": context.user_id,
            "session_id": context.session_id
        }
        
        # 如果有角色配置，添加角色相关信息
        if character:
            data["character_context"] = {
                "name": character.name,
                "role_type": character.role_type.value,
                "expertise": character.expertise_areas,
                "personality": character.personality_traits
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_base}/parse-intent", 
                json=data, 
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # 解析OpenClaw返回的结果
                    intent_type = result.get("intent", {}).get("type", "unknown")
                    confidence = result.get("confidence", 0.7)
                    
                    parsed_result = {
                        "type": intent_type,
                        "intent": user_input,
                        "confidence": confidence,
                        "extra_data": result.get("extra_data", {}),
                        "needs_cloud": True
                    }
                    
                    if character:
                        parsed_result["character_role"] = character.role_type.value
                        
                    return parsed_result
                else:
                    logger.error(f"OpenClaw API request failed with status {response.status}")
                    # 如果OpenClaw解析失败，返回本地规则解析结果
                    return self._rule_based_parse(user_input, character)