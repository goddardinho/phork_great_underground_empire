
from typing import Optional, List, Dict
from objects import GameObject

class Room:
    def __init__(self, id: str, desc_long: str, desc_short: str, exits: Dict[str, str], objects: List[GameObject], flags: List[str] = [], action: Optional[str] = None, locked_exits: Optional[Dict[str, bool]] = None):
        self.id = id
        self.desc_long = desc_long
        self.desc_short = desc_short
        self.exits = exits
        self.objects = objects
        self.flags = flags
        self.action = action
        self.locked_exits = locked_exits if locked_exits is not None else {}

class Player:
    def __init__(self, name: str, current_room: str):
        self.name = name
        self.current_room = current_room
        self.inventory: List[GameObject] = []

class Action:
    def __init__(self, name: str, function):
        self.name = name
        self.function = function  # Callable for action logic
