"""AgentRuntime - 智能体运行时核心"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from .config import ConfigManager
from .character import CharacterManager, CharacterProfile

logger = logging.getLogger(__name__)

@dataclass
class RuntimeContext:
    """运行时上下文，包含用户、设备、会话信息"""
    user_id: str
    session_id: str
    device_id: Optional[str] = None
    character_id: Optional[str] = None  # 新增：角色ID
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentRuntime:
    """智能体运行时核心类
    负责协调意图理解、技能编排和设备控制
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化运行时
        
        Args:
            config: 运行时配置，包含模型设置、技能路径等
        """
        self.config = config or {}
        self.intent_engine = None  # 将在 initialize 中设置
        self.skill_orchestrator = None
        self.device_manager = None
        self.device_registry = None  # 将在 initialize 中创建
        self.device_discovery = None
        self._initialized = False
        self.config_manager = ConfigManager()  # 添加配置管理器
        self.character_manager = CharacterManager()  # 添加角色管理器
        
        logger.info("AgentRuntime initialized with config: %s", self.config)
        logger.info(f"External services configured - LLM: {self.config_manager.has_llm_config()}, "
                   f"Dify: {self.config_manager.has_dify_config()}, "
                   f"OpenClaw: {self.config_manager.has_openclaw_config()}")

    def create_character(self, 
                       user_id: str, 
                       name: str, 
                       role_type: str,
                       description: str = "",
                       llm_config: Optional[Dict[str, Any]] = None,
                       expertise_areas: Optional[list] = None,
                       personality_traits: Optional[list] = None) -> CharacterProfile:
        """创建角色"""
        from .character import CharacterRoleType
        role_enum = CharacterRoleType(role_type)
        return self.character_manager.create_character(
            user_id=user_id,
            name=name,
            role_type=role_enum,
            description=description,
            llm_config=llm_config,
            expertise_areas=expertise_areas,
            personality_traits=personality_traits
        )

    def get_user_characters(self, user_id: str) -> list:
        """获取用户的所有角色"""
        return self.character_manager.get_user_characters(user_id)

    def switch_character(self, user_id: str, character_id: str) -> bool:
        """切换到指定角色"""
        return self.character_manager.switch_character(user_id, character_id)

    def get_character(self, character_id: str) -> Optional[CharacterProfile]:
        """获取角色信息"""
        return self.character_manager.get_character(character_id)
    
    async def initialize(self):
        """异步初始化，加载所有组件"""
        if self._initialized:
            return
        
        logger.info("Initializing AgentRuntime components...")
        
        # 延迟导入避免循环依赖
        from .intent_engine import IntentEngine
        from .orchestrator import SkillOrchestrator
        
        self.intent_engine = IntentEngine(self.config_manager)
        self.skill_orchestrator = SkillOrchestrator(self.config.get("skills", {}))
        
        # 初始化组件
        await self.intent_engine.initialize()
        await self.skill_orchestrator.initialize()
        
        # 初始化设备管理组件
        from src.devices import DeviceRegistry, DeviceDiscovery
        self.device_registry = DeviceRegistry()
        self.device_discovery = DeviceDiscovery()
        
        # 启动设备发现（可选）
        # asyncio.create_task(self._auto_discover())
        logger.info("Device manager initialized")
        
        self._initialized = True
        logger.info("AgentRuntime initialized successfully")
    
    async def process(self, user_input: str, context: RuntimeContext) -> Dict[str, Any]:
        """处理用户输入
        
        Args:
            user_input: 用户输入的自然语言
            context: 运行时上下文
        
        Returns:
            处理结果，包含回答和执行的技能信息
        """
        if not self._initialized:
            await self.initialize()
        
        # 确保intent_engine已初始化
        if self.intent_engine is None:
            raise RuntimeError("Intent engine not initialized")
        
        logger.info("Processing input from user %s: %s", context.user_id, user_input[:50])
        
        # 根据上下文获取角色
        character = None
        if context.character_id:
            character = self.character_manager.get_character(context.character_id)
        else:
            # 如果没有指定角色，则使用默认角色
            character = self.character_manager.get_default_character(context.user_id)
        
        # 1. 意图理解 (传递角色信息)
        intent = await self.intent_engine.parse(user_input, context, character)
        logger.debug("Parsed intent: %s", intent)
        
        # 2. 技能编排
        if self.skill_orchestrator is None:
            raise RuntimeError("Skill orchestrator not initialized")
        
        plan = await self.skill_orchestrator.create_plan(intent, context)
        logger.debug("Created plan: %s", plan)
        
        # 3. 执行计划
        result = await self._execute_plan(plan, context)
        
        return result

    async def _execute_plan(self, plan: Dict, context: RuntimeContext) -> Dict[str, Any]:
        """执行编排好的计划"""
        # 确保skill_orchestrator已经初始化
        assert self.skill_orchestrator is not None, "Skill orchestrator should be initialized"
        
        results = []
        
        for step in plan.get("steps", []):
            skill_name = step.get("skill")
            params = step.get("params", {})
            
            # 调用技能
            step_result = await self.skill_orchestrator.execute_skill(
                skill_name, params, context
            )
            results.append({
                "step": step,
                "result": step_result
            })
        
        return {
            "answer": plan.get("response", "任务执行完成"),
            "results": results,
            "conversation_id": context.session_id
        }
    
    async def execute_device_capability(self, device_id: str, capability: str, **params):
        """执行设备能力"""
        if not self.device_registry:
            return {"error": "Device registry not initialized"}
            
        device = self.device_registry.get_device(device_id)
        if not device:
            return {"error": f"Device {device_id} not found"}
            
        # 将字符串转换为 CapabilityType 枚举
        try:
            from src.devices import CapabilityType
            capability_type = CapabilityType(capability)
        except ValueError:
            return {"error": f"Invalid capability type: {capability}"}
            
        # 假设设备有 execute 方法来执行能力
        return await device.execute(capability_type, **params)
    
    async def shutdown(self):
        """关闭运行时，释放资源"""
        logger.info("Shutting down AgentRuntime...")
        if self.intent_engine:
            await self.intent_engine.shutdown()
        if self.skill_orchestrator:
            await self.skill_orchestrator.shutdown()
        logger.info("AgentRuntime shutdown complete")