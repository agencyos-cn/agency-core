"""角色系统 - 定义专业角色和人格特质"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class CharacterRoleType(Enum):
    """角色类型枚举"""
    TEACHER = "teacher"              # 教育角色
    LAWYER = "lawyer"                # 法律角色
    FINANCIAL_ADVISOR = "financial_advisor"  # 金融顾问
    ASSISTANT = "assistant"          # 个人助理
    DOCTOR = "doctor"                # 医疗顾问
    TECHNICIAN = "technician"        # 技术专家
    CUSTOM = "custom"                # 自定义角色


@dataclass
class CharacterProfile:
    """角色档案 - 定义角色的基本信息和人格特质"""
    # 基础信息
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""  # 角色名称，如"李老师"、"王律师"
    role_type: CharacterRoleType = CharacterRoleType.CUSTOM
    description: str = ""  # 角色描述
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 人格特质
    personality_traits: List[str] = field(default_factory=list)  # 性格特点
    communication_style: str = "professional"  # 沟通风格
    expertise_areas: List[str] = field(default_factory=list)  # 专业领域
    
    # 行为特征
    tone_preference: str = "neutral"  # 语气偏好
    response_length: str = "medium"   # 回复长度（short, medium, long）
    
    # 权限配置
    allowed_skills: List[str] = field(default_factory=list)  # 允许使用的技能
    restricted_actions: List[str] = field(default_factory=list)  # 限制的操作
    
    # 模型配置
    llm_config: Optional[Dict[str, Any]] = field(default_factory=dict)  # 特定的模型配置
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于序列化"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, list):
                result[key] = value
            elif isinstance(value, dict):
                result[key] = value
            else:
                result[key] = value
        return result


class CharacterManager:
    """角色管理器 - 管理用户的所有角色"""
    
    def __init__(self):
        self.characters: Dict[str, CharacterProfile] = {}
        self.default_character_id: Optional[str] = None
        self.user_characters: Dict[str, List[str]] = {}  # 用户ID到角色ID列表的映射

    def create_character(self, 
                       user_id: str, 
                       name: str, 
                       role_type: CharacterRoleType,
                       description: str = "",
                       llm_config: Optional[Dict[str, Any]] = None,
                       expertise_areas: Optional[List[str]] = None,
                       personality_traits: Optional[List[str]] = None,
                       communication_style: str = "professional",
                       tone_preference: str = "neutral",
                       response_length: str = "medium",
                       allowed_skills: Optional[List[str]] = None,
                       restricted_actions: Optional[List[str]] = None) -> CharacterProfile:
        """创建新角色"""
        character = CharacterProfile(
            name=name,
            role_type=role_type,
            description=description,
            expertise_areas=expertise_areas or [],
            personality_traits=personality_traits or [],
            llm_config=llm_config or {},
            communication_style=communication_style,
            tone_preference=tone_preference,
            response_length=response_length,
            allowed_skills=allowed_skills or [],
            restricted_actions=restricted_actions or []
        )
        
        self.characters[character.id] = character
        
        # 将角色关联到用户
        if user_id not in self.user_characters:
            self.user_characters[user_id] = []
        self.user_characters[user_id].append(character.id)
        
        # 如果这是用户创建的第一个角色，设为默认
        if len(self.user_characters[user_id]) == 1:
            self.set_default_character(user_id, character.id)
        
        return character

    def get_character(self, character_id: str) -> Optional[CharacterProfile]:
        """获取角色信息"""
        return self.characters.get(character_id)

    def get_user_characters(self, user_id: str) -> List[CharacterProfile]:
        """获取用户的所有角色"""
        character_ids = self.user_characters.get(user_id, [])
        return [self.characters[char_id] for char_id in character_ids if char_id in self.characters]

    def update_character(self, character_id: str, **kwargs) -> bool:
        """更新角色信息"""
        if character_id not in self.characters:
            return False
            
        character = self.characters[character_id]
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        character.updated_at = datetime.now()
        return True

    def delete_character(self, user_id: str, character_id: str) -> bool:
        """删除角色"""
        if character_id not in self.characters:
            return False
            
        # 从用户角色列表中移除
        if user_id in self.user_characters:
            if character_id in self.user_characters[user_id]:
                self.user_characters[user_id].remove(character_id)
                
                # 如果删除的是默认角色，重新设置默认角色
                if self.default_character_id == character_id:
                    remaining = self.user_characters[user_id]
                    if remaining:
                        self.set_default_character(user_id, remaining[0])
                    else:
                        self.default_character_id = None
        
        # 删除角色
        del self.characters[character_id]
        return True

    def set_default_character(self, user_id: str, character_id: str) -> bool:
        """设置用户的默认角色"""
        if character_id in self.characters:
            self.default_character_id = character_id
            return True
        return False

    def get_default_character(self, user_id: str) -> Optional[CharacterProfile]:
        """获取用户的默认角色"""
        if self.default_character_id and self.default_character_id in self.characters:
            return self.characters[self.default_character_id]
        # 如果没有默认角色，返回用户第一个角色
        user_chars = self.get_user_characters(user_id)
        if user_chars:
            return user_chars[0]
        return None

    def switch_character(self, user_id: str, character_id: str) -> bool:
        """切换到指定角色"""
        if character_id in self.characters:
            self.set_default_character(user_id, character_id)
            return True
        return False
        
    def get_all_role_types(self) -> List[Dict[str, str]]:
        """获取所有可用的角色类型"""
        return [{"value": role.value, "label": self.get_role_display_name(role.value)} for role in CharacterRoleType]
    
    def get_role_display_name(self, role_value: str) -> str:
        """获取角色类型的显示名称"""
        display_names = {
            "teacher": "教师",
            "lawyer": "律师",
            "financial_advisor": "金融顾问",
            "assistant": "个人助理",
            "doctor": "医疗顾问",
            "technician": "技术专家",
            "custom": "自定义角色"
        }
        return display_names.get(role_value, role_value)


# 为向后兼容，定义API类
class CharacterAPI:
    """角色管理API接口，用于前端调用"""
    
    def __init__(self, character_manager: CharacterManager):
        self.manager = character_manager
    
    def list_characters(self, user_id: str) -> Dict[str, Any]:
        """列出用户的所有角色"""
        characters = self.manager.get_user_characters(user_id)
        return {
            "success": True,
            "data": [char.to_dict() for char in characters]
        }
    
    def get_character_detail(self, character_id: str) -> Dict[str, Any]:
        """获取角色详细信息"""
        character = self.manager.get_character(character_id)
        if character:
            return {
                "success": True,
                "data": character.to_dict()
            }
        return {
            "success": False,
            "error": "角色不存在"
        }
    
    def create_character_api(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """API方式创建角色"""
        try:
            character = self.manager.create_character(
                user_id=user_id,
                name=data.get("name", ""),
                role_type=CharacterRoleType(data.get("role_type", "custom")),
                description=data.get("description", ""),
                llm_config=data.get("llm_config"),
                expertise_areas=data.get("expertise_areas", []),
                personality_traits=data.get("personality_traits", []),
                communication_style=data.get("communication_style", "professional"),
                tone_preference=data.get("tone_preference", "neutral"),
                response_length=data.get("response_length", "medium"),
                allowed_skills=data.get("allowed_skills", []),
                restricted_actions=data.get("restricted_actions", [])
            )
            return {
                "success": True,
                "data": character.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_character_api(self, character_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """API方式更新角色"""
        try:
            # 只更新提供的字段
            update_data = {}
            for key in ["name", "role_type", "description", "personality_traits", 
                       "communication_style", "expertise_areas", "tone_preference", 
                       "response_length", "allowed_skills", "restricted_actions", "llm_config"]:
                if key in data:
                    if key == "role_type":
                        update_data[key] = CharacterRoleType(data[key])
                    else:
                        update_data[key] = data[key]
            
            success = self.manager.update_character(character_id, **update_data)
            if success:
                return {
                    "success": True,
                    "data": self.manager.get_character(character_id).to_dict()
                }
            return {
                "success": False,
                "error": "更新失败"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_character_api(self, user_id: str, character_id: str) -> Dict[str, Any]:
        """API方式删除角色"""
        try:
            success = self.manager.delete_character(user_id, character_id)
            if success:
                return {
                    "success": True
                }
            return {
                "success": False,
                "error": "删除失败"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def switch_character_api(self, user_id: str, character_id: str) -> Dict[str, Any]:
        """API方式切换角色"""
        try:
            success = self.manager.switch_character(user_id, character_id)
            if success:
                return {
                    "success": True
                }
            return {
                "success": False,
                "error": "切换失败"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_roles(self) -> Dict[str, Any]:
        """获取所有可用的角色类型"""
        return {
            "success": True,
            "data": self.manager.get_all_role_types()
        }