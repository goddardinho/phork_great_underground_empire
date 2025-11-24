
from __future__ import annotations

class GameObject:
    def __init__(self, name: str, description: str, location: Optional[str] = None, attributes: Optional[dict] = None):
        self.name: str = name
        self.description: str = description
        self.location: Optional[str] = location  # room id or 'inventory'
        self.attributes: dict = attributes if attributes else {}



# Generic .mud file parser
def parse_mud_file(filepath, tag_patterns):
    """
    Parse a .mud file and extract data based on tag_patterns.
    tag_patterns: dict of {tag: regex_pattern}
    Returns: dict of {tag: [matches]}
    """
    import re
    results = {tag: [] for tag in tag_patterns}
    try:
        with open(filepath, "r") as f:
            content = f.read()
        for tag, pattern in tag_patterns.items():
            matches = re.findall(pattern, content)
            results[tag].extend(matches)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    return results

# Example usage for objects, actions, flags, etc.
# tag_patterns = {
#     "object": r'<OBJ\s+"([^"]+)"\s+"([^"]+)"',
#     "action": r'<DEFINE\s+([A-Z0-9_-]+)',
#     "flag": r'<FLAGWORD\s+([\w\s]+)>'
# }
# objects_data = parse_mud_file("zork_mtl_source/prim.mud", tag_patterns)
"""
Phork: A Text-Based Adventure Game
MIT License
Inspired by Zork, written from scratch using only original MDL source as reference.
"""

import sys
from typing import List, Dict, Optional, Any

"""
Core gameplay data structures for Zork-like game.
"""

class Room:
    def __init__(self, id: str, desc_long: str, desc_short: str, exits: Optional[Dict[str, str]] = None, objects: Optional[List["GameObject"]] = None, flags: Optional[List[str]] = None, action: Optional[str] = None):
        self.id: str = id
        self.desc_long: str = desc_long
        self.desc_short: str = desc_short
        self.exits: Dict[str, str] = exits if exits else {}
        self.objects: List["GameObject"] = objects if objects else []
        self.visited: bool = False
        self.flags: List[str] = flags if flags else []
        self.action: Optional[str] = action

# Room definitions extracted from act1.mud
rooms = [
    Room(
        id="EAST-HOUSE",
        desc_long="You are behind the white house. In one corner of the house there is a small window which is open or slightly ajar.",
        desc_short="You are behind the white house. In one corner of the house there is a small window which is open or slightly ajar.",
        exits={"west": "KITCHEN", "south": "LIVING-ROOM"},
        objects=[]
    ),
    Room(
        id="KITCHEN",
        desc_long="You are in the kitchen. There is a window here that is open or slightly ajar.",
        desc_short="You are in the kitchen. There is a window here that is open or slightly ajar.",
        exits={"east": "EAST-HOUSE", "south": "LIVING-ROOM"},
        objects=[GameObject("knife", "A sharp kitchen knife."), GameObject("water", "A glass of water.")]
    ),
    Room(
        id="LIVING-ROOM",
        desc_long="You are in the living room. There is a rug and a trap-door.",
        desc_short="You are in the living room. There is a rug and a trap-door.",
        exits={"north": "KITCHEN", "east": "EAST-HOUSE", "down": "CELLAR"},
        objects=[GameObject("rug", "A large oriental rug."), GameObject("trap-door", "A closed trap-door at your feet."), GameObject("trophy case", "A securely fastened trophy case.")]
    ),
    Room(
        id="CELLAR",
        desc_long="A dark, damp cellar. The trap door crashes shut, and you hear someone barring it.",
        desc_short="A dark, damp cellar. The trap door crashes shut, and you hear someone barring it.",
        exits={"up": "LIVING-ROOM"},
        objects=[GameObject("barrel", "An old wooden barrel."), GameObject("lamp", "A brass lantern.")]
    ),
    Room(
        id="GLACIER-ROOM",
        desc_long="A cold room with a glacier. There is a large passageway leading westward. Part of the glacier may be melted.",
        desc_short="A cold room with a glacier.",
        exits={},
        objects=[]
    ),
    Room(
        id="MIRROR-ROOM",
        desc_long="A room with a large mirror. The mirror may be broken or intact.",
        desc_short="A room with a large mirror.",
        exits={},
        objects=[]
    ),
    Room(
        id="CAROUSEL-ROOM",
        desc_long="You are in a circular room with passages off in eight directions. Your compass needle spins wildly, and you can't get your bearings.",
        desc_short="A circular room with many passages.",
        exits={},
        objects=[]
    ),
    Room(
        id="TORCH-ROOM",
        desc_long="A room with a torch. A large piece of rope descends from the railing above, ending some five feet above your head.",
        desc_short="A room with a torch and rope.",
        exits={},
        objects=[]
    ),
    Room(
        id="DOME-ROOM",
        desc_long="A dome-shaped room. Hanging down from the railing is a rope which ends about ten feet from the floor below.",
        desc_short="A dome-shaped room with a rope.",
        exits={},
        objects=[]
    ),
    Room(
        id="LLD-ROOM",
        desc_long="The Land of the Dead. The way through the gate is barred by evil spirits, who jeer at your attempts to pass.",
        desc_short="The Land of the Dead.",
        exits={},
        objects=[]
    ),
    Room(
        id="LLD2-ROOM",
        desc_long="A room in the Land of the Dead. There may be a pole here.",
        desc_short="A room in the Land of the Dead.",
        exits={},
        objects=[]
    ),
    Room(
        id="DAM-ROOM",
        desc_long="Flood Control Dam #3. There is a control panel here. There is a large metal bolt on the panel. Above the bolt is a small green plastic bubble.",
        desc_short="Flood Control Dam #3.",
        exits={},
        objects=[]
    ),
    Room(
        id="MAINT-ROOM",
        desc_long="Maintenance room. The water level here may change.",
        desc_short="Maintenance room.",
        exits={},
        objects=[]
    ),
    Room(
        id="CYCLOPS-ROOM",
        desc_long="This room has an exit on the west side, and a staircase leading up. The cyclops may be sleeping at the foot of the stairs.",
        desc_short="A room with a cyclops and stairs.",
        exits={},
        objects=[]
    ),
    Room(
        id="ECHO-ROOM",
        desc_long="A room with strange acoustics. The acoustics of the room change subtly.",
        desc_short="A room with strange acoustics.",
        exits={},
        objects=[]
    ),
    Room(
        id="TREASURE-ROOM",
        desc_long="The thief's hideaway. You hear a scream of anguish as you violate the robber's hideaway. Treasures may suddenly vanish.",
        desc_short="The thief's hideaway.",
        exits={},
        objects=[]
    ),
    Room(
        id="LEAPER",
        desc_long="A room where you may need to jump. There may be exits and objects to interact with.",
        desc_short="A room for jumping.",
        exits={},
        objects=[]
    ),
    Room(
        id="CAVE2-ROOM",
        desc_long="A windy cave. Your candles may blow out here.",
        desc_short="A windy cave.",
        exits={},
        objects=[]
    ),
    Room(
        id="CLEARING",
        desc_long="You are in a clearing, with a forest surrounding you on the west and south. There is a grating here.",
        desc_short="You are in a clearing, with a forest surrounding you on the west and south. There is a grating here.",
        exits={},
        objects=[]
    ),
    Room(
        id="MAZE-11",
        desc_long="You are in a small room near the maze. There are twisty passages in the immediate vicinity. Above you is a grating.",
        desc_short="You are in a small room near the maze. There are twisty passages in the immediate vicinity. Above you is a grating.",
        exits={},
        objects=[]
    ),
    Room(
        id="GLACIER-ROOM",
        desc_long="A glacier blocks your way. There is a large passageway leading westward. Part of the glacier may be melted.",
        desc_short="A glacier blocks your way. There is a large passageway leading westward. Part of the glacier may be melted.",
        exits={},
        objects=[]
    ),
    Room(
        id="MIRROR-ROOM",
        desc_long="A room with a large mirror. The mirror may be broken into many pieces.",
        desc_short="A room with a large mirror. The mirror may be broken into many pieces.",
        exits={},
        objects=[]
    ),
    Room(
        id="CAROUSEL-ROOM",
        desc_long="You are in a circular room with passages off in eight directions. Your compass needle spins wildly, and you can't get your bearings.",
        desc_short="You are in a circular room with passages off in eight directions. Your compass needle spins wildly, and you can't get your bearings.",
        exits={},
        objects=[]
    ),
    Room(
        id="TORCH-ROOM",
        desc_long="A room with a torch. A large piece of rope descends from the railing above, ending some five feet above your head.",
        desc_short="A room with a torch. A large piece of rope descends from the railing above, ending some five feet above your head.",
        exits={},
        objects=[]
    ),
    Room(
        id="DOME-ROOM",
        desc_long="A dome room. Hanging down from the railing is a rope which ends about ten feet from the floor below.",
        desc_short="A dome room. Hanging down from the railing is a rope which ends about ten feet from the floor below.",
        exits={},
        objects=[]
    ),
    Room(
        id="LLD-ROOM",
        desc_long="The Land of the Dead. The way through the gate is barred by evil spirits, who jeer at your attempts to pass.",
        desc_short="The Land of the Dead. The way through the gate is barred by evil spirits, who jeer at your attempts to pass.",
        exits={},
        objects=[]
    ),
    Room(
        id="LLD2-ROOM",
        desc_long="Another part of the Land of the Dead. There may be a pole here.",
        desc_short="Another part of the Land of the Dead. There may be a pole here.",
        exits={},
        objects=[]
    ),
    Room(
        id="DAM-ROOM",
        desc_long="Flood Control Dam #3. There is a control panel here. There is a large metal bolt on the panel. Above the bolt is a small green plastic bubble.",
        desc_short="Flood Control Dam #3. There is a control panel here. There is a large metal bolt on the panel. Above the bolt is a small green plastic bubble.",
        exits={},
        objects=[]
    ),
    Room(
        id="RESERVOIR-SOUTH",
        desc_long="You are in a long room, to the north of which was formerly a reservoir. There is a western exit, a passageway south, and a steep pathway climbing up along the edge of a cliff.",
        desc_short="You are in a long room, to the north of which was formerly a reservoir. There is a western exit, a passageway south, and a steep pathway climbing up along the edge of a cliff.",
        exits={},
        objects=[]
    ),
    Room(
        id="RESERVOIR",
        desc_long="You are on what used to be a large reservoir, but which is now a large mud pile. There are 'shores' to the north and south.",
        desc_short="You are on what used to be a large reservoir, but which is now a large mud pile. There are 'shores' to the north and south.",
        exits={},
        objects=[]
    ),
    Room(
        id="RESERVOIR-NORTH",
        desc_long="You are in a large cavernous room, north of a large reservoir. There is a tunnel leaving the room to the north.",
        desc_short="You are in a large cavernous room, north of a large reservoir. There is a tunnel leaving the room to the north.",
        exits={},
        objects=[]
    ),
    Room(
        id="CYCLOPS-ROOM",
        desc_long="This room has an exit on the west side, and a staircase leading up. The cyclops may be sleeping blissfully at the foot of the stairs.",
        desc_short="This room has an exit on the west side, and a staircase leading up. The cyclops may be sleeping blissfully at the foot of the stairs.",
        exits={},
        objects=[]
    ),
    Room(
        id="ECHO-ROOM",
        desc_long="A room with strange acoustics. The acoustics of the room change subtly.",
        desc_short="A room with strange acoustics. The acoustics of the room change subtly.",
        exits={},
        objects=[]
    ),
    Room(
        id="TREASURE-ROOM",
        desc_long="The robber's hideaway. You hear a scream of anguish as you violate the robber's hideaway. Treasures may be here.",
        desc_short="The robber's hideaway. You hear a scream of anguish as you violate the robber's hideaway. Treasures may be here.",
        exits={},
        objects=[]
    ),
    Room(
        id="CAVE2-ROOM",
        desc_long="A cave. The cave is very windy at the moment and your candles have blown out.",
        desc_short="A cave. The cave is very windy at the moment and your candles have blown out.",
        exits={},
        objects=[]
    ),
]



class Player:
    def __init__(self, name: str, current_room: str):
        self.name = name
        self.current_room = current_room
        self.inventory: List[GameObject] = []

class Action:
    def __init__(self, name: str, function):
        self.name = name
        self.function = function  # Callable for action logic

# Example usage (to be expanded in later steps)

actions: Dict[str, Action] = {}
player: Optional[Player] = None

class Game:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.current_room: Optional[str] = None
        self.inventory: List[GameObject] = []

    def parse_command(self, command: str):
        command = command.strip().lower()
        directions = ["north", "south", "east", "west"]
        if command in directions:
            self.move(command)
            return
        if command in ["look"]:
            self.describe()
            return
        if command in ["quit", "exit"]:
            print("Thanks for playing Phork!")
            exit(0)
        print("I don't understand that command.")

    def describe(self):
        room = self.rooms[self.current_room]
        print(f"\n{room.id}\n{room.desc_long}")
        print("Exits: " + ", ".join(room.exits.keys()))

    def move(self, direction):
        room = self.rooms[self.current_room]
        if direction in room.exits:
            self.current_room = room.exits[direction]
            self.describe()
        else:
            print("You can't go that way.")

    def run(self):
        self.describe()
        while True:
            try:
                command = input("\n> ")
                self.parse_command(command)
            except (EOFError, KeyboardInterrupt):
                print("\nThanks for playing Phork!")
                break


import re


# Expandable tag parsers
def parse_exits(line):
    exits = {}
    matches = re.findall(r'<EXIT\s+"(\w+)"\s+"([^"]+)"', line)
    for direction, dest in matches:
        exits[direction] = dest
    return exits

def parse_objects(line):
    objects = []
    matches = re.findall(r'<OBJ\s+"([^"]+)"\s+"([^"]+)"(?:\s+([\w\s]+))?', line)
    for match in matches:
        name, desc, *rest = match
        obj = GameObject(name, desc)
        # Future: parse additional attributes from rest
        objects.append(obj)
    return objects

def parse_flags(line):
    # Example: <FLAGWORD RSEENBIT RLIGHTBIT ...>
    flags = re.findall(r'<FLAGWORD\s+([\w\s]+)>', line)
    return flags[0].split() if flags else []

def parse_action(line):
    # Example: <RACTION "some_action">
    match = re.search(r'<RACTION\s+"([^"]+)"', line)
    return match.group(1) if match else None

def load_rooms():
    rooms = {}
    try:
        with open("zork_mtl_source/rooms.mud", "r") as f:
            lines = f.readlines()
        room_id: Optional[str] = None
        desc_long: Optional[str] = None
        desc_short: Optional[str] = None
        exits: Dict[str, str] = {}
        objects: List[GameObject] = []
        flags: List[str] = []
        action: Optional[str] = None
        for line in lines:
            line = line.strip()
            if line.startswith('<ROOM'):
                if room_id:
                    room = Room(room_id, desc_long or "", desc_short or "", exits, objects, flags, action)
                    rooms[room_id] = room
                parts = line.split('"')
                room_id = parts[1] if len(parts) > 1 else None
                desc_long = None
                desc_short = None
                exits = {}
                objects = []
                flags = []
                action = None
            elif room_id and line.startswith('"'):
                if not desc_long:
                    desc_long = line.strip('"')
                elif not desc_short:
                    desc_short = line.strip('"')
            elif room_id and '<EXIT' in line:
                exits.update(parse_exits(line))
            elif room_id and '<OBJ' in line:
                objects.extend(parse_objects(line))
            elif room_id and '<FLAGWORD' in line:
                flags.extend(parse_flags(line))
            elif room_id and '<RACTION' in line:
                action = parse_action(line)
        if room_id:
            room = Room(room_id, desc_long or "", desc_short or "", exits, objects, flags, action)
            rooms[room_id] = room
    except Exception as e:
        print(f"Error loading rooms: {e}. Using fallback rooms.")
        rooms["West of House"] = Room(
            "West of House",
            "You are standing in an open field west of a white house, with a boarded front door.",
            "Field west of house.",
            {"east": "Kitchen"}
        )
        rooms["Kitchen"] = Room(
            "Kitchen",
            "You are in the kitchen. There is a table here.",
            "Kitchen.",
            {"west": "West of House"}
        )
    return rooms


# Import auto-generated rooms
try:
    from rooms import create_rooms
    auto_rooms = create_rooms()
except ImportError:
    auto_rooms = {}

def main():
    game = Game()
    # Use auto-generated rooms if available, else fallback
    game.rooms = auto_rooms if auto_rooms else load_rooms()
    # Start in a known room if present, else fallback
    game.current_room = next(iter(game.rooms.keys()), "West of House")
    game.run()
