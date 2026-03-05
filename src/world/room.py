"""Room class - Represents a game location."""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class Room:
    """Represents a single location in the game world."""
    
    id: str
    name: str
    description: str
    exits: Dict[str, str] = field(default_factory=dict)  # direction -> room_id
    items: List[str] = field(default_factory=list)  # item IDs in this room
    flags: Set[str] = field(default_factory=set)  # room properties (dark, etc.)
    visited: bool = False
    
    def get_exit(self, direction: str) -> Optional[str]:
        """Get the room ID for a given direction, if exit exists."""
        return self.exits.get(direction.lower())
    
    def add_item(self, item_id: str) -> None:
        """Add an item to this room."""
        if item_id not in self.items:
            self.items.append(item_id)
    
    def remove_item(self, item_id: str) -> bool:
        """Remove an item from this room. Returns True if item was present."""
        try:
            self.items.remove(item_id)
            return True
        except ValueError:
            return False
    
    def has_flag(self, flag: str) -> bool:
        """Check if room has a specific flag."""
        return flag in self.flags
    
    def get_description(self, is_brief: bool = False) -> str:
        """Get room description. Brief mode shows just the name if visited."""
        if is_brief and self.visited:
            return self.name
        return f"{self.name}\n\n{self.description}"