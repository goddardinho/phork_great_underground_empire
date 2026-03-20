"""ObjectManager - Central registry for all game objects."""

from typing import Dict, Optional, List, Tuple
from .objects import GameObject


class ObjectManager:
    """Manages all game objects and their locations."""
    
    def __init__(self) -> None:
        self.objects: Dict[str, GameObject] = {}
    
    def add_object(self, obj: GameObject) -> None:
        """Add an object to the registry."""
        self.objects[obj.id] = obj
    
    def get_object(self, object_id: str) -> Optional[GameObject]:
        """Get an object by its ID."""
        return self.objects.get(object_id)
    
    def find_objects_by_name(self, name: str) -> List[GameObject]:
        """Find all objects that match the given name."""
        matches = []
        for obj in self.objects.values():
            if obj.matches(name):
                matches.append(obj)
        return matches
    
    def get_objects_in_room(self, room_items: List[str]) -> List[GameObject]:
        """Get GameObject instances for object IDs in a room."""
        objects = []
        for item_id in room_items:
            obj = self.get_object(item_id)
            if obj:
                objects.append(obj)
        return objects
    
    def get_objects_in_inventory(self, inventory: List[str]) -> List[GameObject]:
        """Get GameObject instances for object IDs in inventory."""
        objects = []
        for item_id in inventory:
            obj = self.get_object(item_id)
            if obj:
                objects.append(obj)
        return objects
    
    def find_object_location(self, obj: GameObject, world, player) -> Tuple[str, Optional[str]]:
        """Find where an object is located. Returns (location_type, container_id)."""
        from ..world.world import World
        from ..entities.player import Player
        
        current_room = world.get_room(player.current_room)
        
        # Check if in current room
        if current_room and obj.id in current_room.items:
            return ("room", None)
        
        # Check if in inventory
        if obj.id in player.inventory:
            return ("inventory", None)
        
        # Check if in containers in current room
        if current_room:
            for item_id in current_room.items:
                container = self.get_object(item_id)
                if container and container.is_container() and obj.id in container.get_contents():
                    return ("container", container.id)
        
        # Check if in containers in inventory
        for item_id in player.inventory:
            container = self.get_object(item_id)
            if container and container.is_container() and obj.id in container.get_contents():
                return ("container", container.id)
        
        return ("unknown", None)
    
    def get_all_objects(self) -> Dict[str, GameObject]:
        """Get all objects in the registry."""
        return self.objects.copy()
    
    def __len__(self) -> int:
        """Return number of objects in registry."""
        return len(self.objects)