"""Entities module - Contains Player, GameObject, NPC, and Combat classes."""

from .player import Player
from .objects import GameObject
from .npc import NPC, DialogueNode, DialogueResponse
from .npc_manager import NPCManager
from .object_manager import ObjectManager
from .object_loader import ZorkObjectLoader
from .combat import (
    CombatManager, 
    CombatStats, 
    CombatAction, 
    CombatResult, 
    WeaponType, 
    WEAPON_STATS
)

__all__ = [
    # Core entities
    'Player',
    'GameObject', 
    'NPC',
    'DialogueNode',
    'DialogueResponse',
    
    # Managers
    'NPCManager',
    'ObjectManager',
    'ZorkObjectLoader',
    
    # Combat system
    'CombatManager',
    'CombatStats',
    'CombatAction', 
    'CombatResult',
    'WeaponType',
    'WEAPON_STATS'
]