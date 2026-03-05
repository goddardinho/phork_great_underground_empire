"""World class - Contains and manages all rooms."""

from typing import Dict, Optional, List
from .room import Room


class World:
    """Contains and manages all game rooms and their relationships."""
    
    def __init__(self) -> None:
        self.rooms: Dict[str, Room] = {}
    
    def add_room(self, room: Room) -> None:
        """Add a room to the world."""
        self.rooms[room.id] = room
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by its ID."""
        return self.rooms.get(room_id)
    
    def validate_exits(self) -> List[str]:
        """Validate that all exits point to existing rooms. Returns list of errors."""
        errors = []
        for room in self.rooms.values():
            for direction, target_id in room.exits.items():
                if target_id not in self.rooms:
                    errors.append(f"Room {room.id}: Exit '{direction}' points to non-existent room '{target_id}'")
        return errors
    
    def get_rooms_with_flag(self, flag: str) -> List[Room]:
        """Get all rooms that have a specific flag."""
        return [room for room in self.rooms.values() if room.has_flag(flag)]
    
    def __len__(self) -> int:
        """Return number of rooms in the world."""
        return len(self.rooms)