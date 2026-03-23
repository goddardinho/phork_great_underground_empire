"""Combat system for NPCs and player interactions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .objects import GameObject
    from .npc import NPC
    from .player import Player


class CombatResult(Enum):
    """Result of a combat action."""
    HIT = "hit"
    MISS = "miss"
    CRITICAL = "critical"
    BLOCK = "block"
    DODGE = "dodge"
    DEATH = "death"
    FLEE = "flee"


@dataclass
class CombatStats:
    """Combat statistics for entities."""
    max_health: int = 100
    current_health: int = 100
    attack_power: int = 10
    defense: int = 5
    accuracy: int = 80  # Percentage
    dodge_chance: int = 15  # Percentage
    block_chance: int = 10  # Percentage
    critical_chance: int = 5  # Percentage
    weapon: Optional['GameObject'] = None

    def is_alive(self) -> bool:
        """Check if entity is still alive."""
        return self.current_health > 0
    
    def take_damage(self, damage: int) -> int:
        """Apply damage and return actual damage taken."""
        actual_damage = max(0, damage - self.defense)
        self.current_health = max(0, self.current_health - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal and return actual amount healed."""
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - old_health
    
    def get_attack_damage(self) -> int:
        """Calculate attack damage including weapon bonuses."""
        base_damage = self.attack_power
        
        # Add weapon damage if equipped
        if self.weapon and hasattr(self.weapon, 'damage'):
            base_damage += self.weapon.damage
        
        # Add some randomness (±20%)
        variation = int(base_damage * 0.2)
        damage = base_damage + random.randint(-variation, variation)
        
        return max(1, damage)  # Minimum 1 damage


@dataclass 
class CombatAction:
    """Represents a combat action and its result."""
    attacker: str  # Name of attacking entity
    target: str    # Name of target entity
    action_type: str  # "attack", "defend", "flee", etc.
    result: CombatResult
    damage: int = 0
    description: str = ""
    timestamp: float = field(default_factory=lambda: __import__('time').time())


class CombatManager:
    """Manages combat encounters between player and NPCs."""
    
    def __init__(self):
        self.active_combats: Dict[str, Dict] = {}  # room_id -> combat_state
        self.combat_history: List[CombatAction] = []
        self.max_history_size = 50
        
    def start_combat(self, attacker_id: str, target_id: str, room_id: str) -> bool:
        """Start combat between two entities."""
        if room_id in self.active_combats:
            return False  # Combat already active in this room
        
        self.active_combats[room_id] = {
            'participants': [attacker_id, target_id],
            'turn_order': [attacker_id, target_id],
            'current_turn': 0,
            'round_number': 1,
            'start_time': __import__('time').time()
        }
        
        return True
    
    def end_combat(self, room_id: str, winner: Optional[str] = None) -> Dict:
        """End combat in a room and return results."""
        if room_id not in self.active_combats:
            return {}
        
        combat_data = self.active_combats.pop(room_id)
        combat_data['end_time'] = __import__('time').time()
        combat_data['duration'] = combat_data['end_time'] - combat_data['start_time']
        combat_data['winner'] = winner
        
        return combat_data
    
    def is_in_combat(self, room_id: str) -> bool:
        """Check if combat is active in a room."""
        return room_id in self.active_combats
    
    def get_combat_participants(self, room_id: str) -> List[str]:
        """Get list of combat participants in a room."""
        if room_id not in self.active_combats:
            return []
        return self.active_combats[room_id]['participants'].copy()
    
    def calculate_attack(self, attacker_stats: CombatStats, defender_stats: CombatStats) -> Tuple[CombatResult, int]:
        """Calculate the result of an attack."""
        # Check if attack hits
        hit_chance = attacker_stats.accuracy - (defender_stats.dodge_chance // 2)
        hit_roll = random.randint(1, 100)
        
        # Miss check
        if hit_roll > hit_chance:
            return CombatResult.MISS, 0
        
        # Dodge check
        if random.randint(1, 100) <= defender_stats.dodge_chance:
            return CombatResult.DODGE, 0
        
        # Block check
        if random.randint(1, 100) <= defender_stats.block_chance:
            return CombatResult.BLOCK, 0
        
        # Calculate damage
        damage = attacker_stats.get_attack_damage()
        
        # Critical hit check
        if random.randint(1, 100) <= attacker_stats.critical_chance:
            damage = int(damage * 1.5)
            return CombatResult.CRITICAL, damage
        
        return CombatResult.HIT, damage
    
    def execute_attack(self, attacker_stats: CombatStats, defender_stats: CombatStats, 
                      attacker_name: str, defender_name: str) -> CombatAction:
        """Execute an attack between two entities."""
        result, damage = self.calculate_attack(attacker_stats, defender_stats)
        
        # Apply damage if hit
        actual_damage = 0
        if result in [CombatResult.HIT, CombatResult.CRITICAL]:
            actual_damage = defender_stats.take_damage(damage)
            
            # Check for death
            if not defender_stats.is_alive():
                result = CombatResult.DEATH
        
        # Create description based on result
        description = self._generate_combat_description(
            attacker_name, defender_name, result, actual_damage, attacker_stats.weapon
        )
        
        # Record the action
        action = CombatAction(
            attacker=attacker_name,
            target=defender_name,
            action_type="attack",
            result=result,
            damage=actual_damage,
            description=description
        )
        
        self._add_to_history(action)
        return action
    
    def attempt_flee(self, fleeing_entity: str, room_id: str) -> bool:
        """Attempt to flee from combat."""
        if room_id not in self.active_combats:
            return True  # Not in combat, can always "flee"
        
        # Base 70% chance to flee, modified by circumstances
        flee_chance = 70
        
        # TODO: Modify based on entity stats, room conditions, etc.
        
        success = random.randint(1, 100) <= flee_chance
        
        if success:
            # Remove from combat participants
            participants = self.active_combats[room_id]['participants']
            if fleeing_entity in participants:
                participants.remove(fleeing_entity)
            
            # End combat if only one participant left
            if len(participants) <= 1:
                remaining = participants[0] if participants else None
                self.end_combat(room_id, winner=remaining)
        
        return success
    
    def get_combat_status(self, room_id: str) -> Optional[Dict]:
        """Get current combat status for a room."""
        if room_id not in self.active_combats:
            return None
        
        combat = self.active_combats[room_id].copy()
        combat['is_active'] = True
        return combat
    
    def _generate_combat_description(self, attacker: str, defender: str, 
                                   result: CombatResult, damage: int, 
                                   weapon: Optional['GameObject'] = None) -> str:
        """Generate descriptive text for combat actions."""
        weapon_name = weapon.name if weapon else "fists"
        
        if result == CombatResult.MISS:
            return f"{attacker} swings at {defender} with {weapon_name} but misses completely!"
        elif result == CombatResult.DODGE:
            return f"{defender} dodges {attacker}'s attack with {weapon_name}!"
        elif result == CombatResult.BLOCK:
            return f"{defender} blocks {attacker}'s attack with {weapon_name}!"
        elif result == CombatResult.HIT:
            return f"{attacker} strikes {defender} with {weapon_name} for {damage} damage!"
        elif result == CombatResult.CRITICAL:
            return f"{attacker} delivers a devastating blow to {defender} with {weapon_name} for {damage} damage!"
        elif result == CombatResult.DEATH:
            return f"{attacker}'s attack with {weapon_name} defeats {defender} completely!"
        else:
            return f"{attacker} attacks {defender} with {weapon_name}."
    
    def _add_to_history(self, action: CombatAction):
        """Add action to combat history."""
        self.combat_history.append(action)
        
        # Trim history if too long
        if len(self.combat_history) > self.max_history_size:
            self.combat_history = self.combat_history[-self.max_history_size:]
    
    def get_recent_actions(self, count: int = 5) -> List[CombatAction]:
        """Get recent combat actions."""
        return self.combat_history[-count:] if self.combat_history else []
    
    def clear_history(self):
        """Clear combat history."""
        self.combat_history.clear()


class WeaponType(Enum):
    """Types of weapons with different characteristics."""
    BARE_HANDS = "bare_hands"
    SWORD = "sword"
    AXE = "axe"
    DAGGER = "dagger"
    STAFF = "staff"
    BOW = "bow"
    CLUB = "club"


# Weapon damage multipliers and special properties
WEAPON_STATS = {
    WeaponType.BARE_HANDS: {"damage": 0, "accuracy": 0, "critical": 0},
    WeaponType.SWORD: {"damage": 15, "accuracy": 10, "critical": 5},
    WeaponType.AXE: {"damage": 20, "accuracy": -5, "critical": 10},
    WeaponType.DAGGER: {"damage": 8, "accuracy": 15, "critical": 15},
    WeaponType.STAFF: {"damage": 12, "accuracy": 5, "critical": 2},
    WeaponType.BOW: {"damage": 18, "accuracy": 20, "critical": 8},
    WeaponType.CLUB: {"damage": 14, "accuracy": -2, "critical": 3},
}