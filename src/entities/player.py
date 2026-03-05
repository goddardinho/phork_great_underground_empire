"""Player class - Represents the player character."""

from typing import List, Optional
from .objects import GameObject


class Player:
    """Represents the player character and their state."""
    
    def __init__(self, start_room: str = "WHOUS") -> None:
        self.current_room: str = start_room
        self.inventory: List[str] = []  # List of object IDs
        self.score: int = 0
        self.max_inventory_size: int = 10
        self.brief_mode: bool = False  # Whether to show brief room descriptions
        
        # Disambiguation state
        self.awaiting_disambiguation: bool = False
        self.disambiguation_options: List['GameObject'] = []
        self.pending_command: Optional[str] = None  # The original command waiting for disambiguation
        
        # Disambiguation state
        self.awaiting_disambiguation: bool = False
        self.disambiguation_options: List[GameObject] = []
        self.pending_command: Optional[str] = None  # The original command waiting for disambiguation
        
    def add_to_inventory(self, item_id: str) -> bool:
        """Add an item to inventory. Returns True if successful."""
        if len(self.inventory) >= self.max_inventory_size:
            return False
        if item_id not in self.inventory:
            self.inventory.append(item_id)
        return True
    
    def remove_from_inventory(self, item_id: str) -> bool:
        """Remove an item from inventory. Returns True if item was present."""
        try:
            self.inventory.remove(item_id)
            return True
        except ValueError:
            return False
    
    def has_item(self, item_id: str) -> bool:
        """Check if player has a specific item."""
        return item_id in self.inventory
    
    def move_to_room(self, room_id: str) -> None:
        """Move player to a different room."""
        self.current_room = room_id
    
    def get_inventory_count(self) -> int:
        """Get number of items in inventory."""
        return len(self.inventory)
    
    def is_inventory_full(self) -> bool:
        """Check if inventory is at capacity."""
        return len(self.inventory) >= self.max_inventory_size