"""AgencyOS 核心模块"""

from .core.runtime import AgentRuntime
from .core.character import CharacterManager, CharacterProfile, CharacterRoleType
from .skills import BaseSkill, SkillRegistry
from .devices import DeviceRegistry

__version__ = "0.1.0"
__author__ = "AgencyOS Contributors"
__all__ = [
    "AgentRuntime", 
    "CharacterManager", 
    "CharacterProfile", 
    "CharacterRoleType",
    "BaseSkill",
    "SkillRegistry",
    "DeviceRegistry"
]