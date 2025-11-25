from typing import Optional, List, Dict

class GameObject:
    def __init__(self, name: str, description: str, location: Optional[str] = None, attributes: Optional[dict] = None):
        self.name = name
        self.description = description
        self.location = location
        self.attributes = attributes if attributes else {}

class Room:
    def __init__(self, id: str, desc_long: str, desc_short: str, exits: Dict[str, str], objects: List[GameObject], flags: List[str] = [], action: Optional[str] = None):
        self.id = id
        self.desc_long = desc_long
        self.desc_short = desc_short
        self.exits = exits
        self.objects = objects
        self.flags = flags
        self.action = action

class Player:
    def __init__(self, name: str, current_room: str):
        self.name = name
        self.current_room = current_room
        self.inventory: List[GameObject] = []

class Action:
    def __init__(self, name: str, function):
        self.name = name
        self.function = function  # Callable for action logic
