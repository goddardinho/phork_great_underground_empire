"""NPC (Non-Player Character) entity classes for Zork."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from .combat import CombatStats


@dataclass
class DialogueResponse:
    """A possible response option in a dialogue."""
    id: str
    text: str  # What the player says
    next_node: str  # Next dialogue node ID
    conditions: List[str] = field(default_factory=list)  # Requirements to show this option


@dataclass
class DialogueNode:
    """A single node in a dialogue tree."""
    id: str
    text: str  # What the NPC says
    responses: List[DialogueResponse] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)  # Requirements to reach this node
    effects: List[str] = field(default_factory=list)  # State changes after this node
    end_conversation: bool = False  # Whether this node ends the conversation


@dataclass
class NPC:
    """Represents a Non-Player Character in the game world."""
    
    id: str
    name: str  # Primary name players use
    description: str  # Description when examined or seen in room
    location: str  # Current room ID
    dialogue_tree: Dict[str, DialogueNode] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)  # NPC internal state
    aliases: List[str] = field(default_factory=list)  # Alternative names
    attributes: Dict[str, Any] = field(default_factory=dict)  # NPC properties
    
    # Combat stats - default to moderate NPC stats
    combat_stats: CombatStats = field(default_factory=lambda: CombatStats(
        max_health=80,
        current_health=80,
        attack_power=12,
        defense=5,
        accuracy=75,
        dodge_chance=15,
        block_chance=10,  
        critical_chance=5
    ))
    
    def get_attribute(self, name: str, default: Any = None) -> Any:
        """Get an attribute value with optional default."""
        return self.attributes.get(name, default)
    
    def set_attribute(self, name: str, value: Any) -> None:
        """Set an attribute value."""
        self.attributes[name] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value with optional default."""
        return self.state.get(key, default)
    
    def set_state(self, key: str, value: Any) -> None:
        """Set a state value."""
        self.state[key] = value
    
    def is_moveable(self) -> bool:
        """Check if this NPC can move between rooms."""
        return self.get_attribute("moveable", False)
    
    def is_hostile(self) -> bool:
        """Check if this NPC is hostile to the player."""
        return self.get_attribute("hostile", False)
    
    def is_friendly(self) -> bool:
        """Check if this NPC is friendly to the player."""
        return self.get_attribute("friendly", True)
    
    def matches(self, name: str) -> bool:
        """Check if the given name matches this NPC's name or aliases."""
        name_lower = name.lower().strip()
        
        # Check primary name
        if name_lower == self.name.lower():
            return True
            
        # Check aliases
        for alias in self.aliases:
            if name_lower == alias.lower():
                return True
        
        # Check if name is a substring of the primary name (for partial matches)
        if len(name_lower) >= 3 and name_lower in self.name.lower():
            return True
                
        return False
    
    def get_dialogue_node(self, node_id: str) -> Optional[DialogueNode]:
        """Get a dialogue node by ID."""
        return self.dialogue_tree.get(node_id)
    
    def get_greeting_node(self) -> Optional[DialogueNode]:
        """Get the default greeting node for starting conversations."""
        # Try to find a greeting node, fallback to first available node
        if "greeting" in self.dialogue_tree:
            return self.dialogue_tree["greeting"]
        elif "start" in self.dialogue_tree:
            return self.dialogue_tree["start"]
        elif self.dialogue_tree:
            return next(iter(self.dialogue_tree.values()))
        return None
    
    def __str__(self) -> str:
        """String representation for display."""
        return self.name