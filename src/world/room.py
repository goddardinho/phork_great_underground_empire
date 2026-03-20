"""Room class - Represents a game location."""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class Room:
    """Represents a single location in the game world."""
    
    # Room flag constants for backward compatibility
    ROOM_DARK = "dark"
    ROOM_VISITED = "visited" 
    ROOM_DEADLY = "deadly"
    ROOM_SACRED = "sacred"
    ROOM_OUTDOOR = "outdoor"
    ROOM_WATER = "water"
    
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
    
    def set_flag(self, flag: str) -> None:
        """Set a flag on this room."""
        self.flags.add(flag)
    
    def clear_flag(self, flag: str) -> None:
        """Clear a flag from this room."""
        self.flags.discard(flag)
    
    def get_description(self, force_brief: bool = False, force_verbose: bool = False, include_name: bool = True) -> str:
        """
        Get room description based on visit status and preferences.
        
        Args:
            force_brief: If True, always show brief description (just name)
            force_verbose: If True, always show full description
            include_name: If True, include room name in output (default True for compatibility)
        
        Returns:
            Formatted room description
        """
        # Force brief shows just the name (when brief mode is on and room visited)
        if force_brief and self.visited:
            return self.name
        
        # Handle empty descriptions gracefully
        description = self.description if self.description else self.name
        
        # Force verbose or default: show full description, optionally with name
        if include_name:
            return f"{self.name}\n\n{description}"
        else:
            return description