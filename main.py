
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
        id="MIRROR-ROOM",
        desc_long="A room with a large mirror. The mirror may be broken into many pieces if destroyed. There is an ugly person staring back at you, or the mirror is shattered.",
        desc_short="A room with a large mirror.",
        exits={},
        objects=[GameObject("mirror", "A large mirror, possibly broken.")]
    ),
    Room(
        id="TORCH-ROOM",
        desc_long="A room with a torch. A large piece of rope descends from the railing above, ending some five feet above your head.",
        desc_short="Torch room with rope.",
        exits={},
        objects=[GameObject("torch", "A burning torch."), GameObject("rope", "A rope hanging from the railing.")]
    ),
    Room(
        id="DOME-ROOM",
        desc_long="A dome-shaped room. Hanging down from the railing is a rope which ends about ten feet from the floor below. Jumping may be dangerous here.",
        desc_short="Dome room with rope.",
        exits={},
        objects=[GameObject("rope", "A rope hanging from the railing.")]
    ),
    Room(
        id="LLD2-ROOM",
        desc_long="A room in the Land of the Dead. If you are on the pole, you see a different description.",
        desc_short="Land of the Dead (2).",
        exits={},
        objects=[GameObject("pole", "A mysterious pole.")]
    ),
    Room(
        id="DAM-ROOM",
        desc_long="Flood Control Dam #3. There is a control panel here, a large metal bolt, and a small green plastic bubble. The bubble may glow depending on the gate state.",
        desc_short="Flood Control Dam #3.",
        exits={},
        objects=[GameObject("control panel", "A dam control panel."), GameObject("metal bolt", "A large metal bolt."), GameObject("green bubble", "A small green plastic bubble.")]
    ),
    Room(
        id="CYCLOPS-ROOM",
        desc_long="This room has an exit on the west side, and a staircase leading up. The cyclops may be sleeping, angry, or have a hole in the north wall depending on game state.",
        desc_short="Cyclops room with stairs.",
        exits={"west": "CYCLOPS-WEST-ROOM", "up": "CYCLOPS-UP-STAIRS"},
        objects=[GameObject("cyclops", "A sleeping or angry cyclops.")]
    ),
    Room(
        id="TREASURE-ROOM",
        desc_long="The thief's hideaway. You hear a scream of anguish as you violate the robber's hideaway. Treasures may vanish mysteriously.",
        desc_short="Thief's treasure room.",
        exits={},
        objects=[GameObject("treasure", "Various treasures."), GameObject("thief", "A mysterious thief.")]
    ),
    Room(
        id="MAINT-ROOM",
        desc_long="Maintenance room. The water level here may change.",
        desc_short="Maintenance room.",
        exits={"east": "DAM-ROOM"},
        objects=[GameObject("toolbox", "A rusty toolbox."), GameObject("wrench", "A heavy wrench.")],
        flags=["maintenance"],
        action=None
    ),
    Room(
        id="ECHO-ROOM",
        desc_long="A room with strange acoustics. The acoustics of the room change subtly.",
        desc_short="A room with strange acoustics.",
        exits={"north": "MAZE-11", "south": "CAVE2-ROOM"},
        objects=[],
        flags=["echo"],
        action=None
    ),
    Room(
        id="LEAPER",
        desc_long="A room where you may need to jump. There may be exits and objects to interact with.",
        desc_short="A room for jumping.",
        exits={"up": "DOME-ROOM"},
        objects=[GameObject("ledge", "A narrow ledge.")],
        flags=["jump"],
        action=None
    ),
    Room(
        id="CAVE2-ROOM",
        desc_long="A windy cave. Your candles may blow out here.",
        desc_short="A windy cave.",
        exits={"west": "ECHO-ROOM"},
        objects=[GameObject("candle", "A candle, possibly blown out.")],
        flags=["windy"],
        action=None
    ),
    Room(
        id="CLEARING",
        desc_long="You are in a clearing, with a forest surrounding you on the west and south. There is a grating here.",
        desc_short="You are in a clearing, with a forest surrounding you on the west and south. There is a grating here.",
        exits={"north": "FOREST", "east": "HOUSE"},
        objects=[GameObject("grating", "A metal grating.")],
        flags=["outdoors"],
        action=None
    ),
    Room(
        id="MAZE-11",
        desc_long="You are in a small room near the maze. There are twisty passages in the immediate vicinity. Above you is a grating.",
        desc_short="You are in a small room near the maze. There are twisty passages in the immediate vicinity. Above you is a grating.",
        exits={"south": "ECHO-ROOM"},
        objects=[GameObject("grating", "A metal grating above.")],
        flags=["maze"],
        action=None
    ),
    Room(
        id="GLACIER-ROOM",
        desc_long="A glacier blocks your way. There is a large passageway leading westward. Part of the glacier may be melted.",
        desc_short="A glacier blocks your way. There is a large passageway leading westward. Part of the glacier may be melted.",
        exits={"west": "CAVE2-ROOM"},
        objects=[GameObject("glacier", "A massive glacier.")],
        flags=["cold"],
        action=None
    ),
    Room(
        id="CAROUSEL-ROOM",
        desc_long="You are in a circular room with passages off in eight directions. Your compass needle spins wildly, and you can't get your bearings.",
        desc_short="You are in a circular room with passages off in eight directions. Your compass needle spins wildly, and you can't get your bearings.",
        exits={"north": "MAZE-11", "south": "GLACIER-ROOM"},
        objects=[GameObject("compass", "A spinning compass needle.")],
        flags=["carousel"],
        action=None
    ),
    Room(
        id="RESERVOIR-SOUTH",
        desc_long="You are in a long room, to the north of which was formerly a reservoir. There is a western exit, a passageway south, and a steep pathway climbing up along the edge of a cliff.",
        desc_short="You are in a long room, to the north of which was formerly a reservoir. There is a western exit, a passageway south, and a steep pathway climbing up along the edge of a cliff.",
        exits={"west": "RESERVOIR", "south": "RESERVOIR-NORTH"},
        objects=[],
        flags=["water"],
        action=None
    ),
    Room(
        id="RESERVOIR",
        desc_long="You are on what used to be a large reservoir, but which is now a large mud pile. There are 'shores' to the north and south.",
        desc_short="You are on what used to be a large reservoir, but which is now a large mud pile. There are 'shores' to the north and south.",
        exits={"north": "RESERVOIR-NORTH", "south": "RESERVOIR-SOUTH"},
        objects=[GameObject("mud", "A large mud pile.")],
        flags=["water"],
        action=None
    ),
    Room(
        id="RESERVOIR-NORTH",
        desc_long="You are in a large cavernous room, north of a large reservoir. There is a tunnel leaving the room to the north.",
        desc_short="You are in a large cavernous room, north of a large reservoir. There is a tunnel leaving the room to the north.",
        exits={"north": "TUNNEL", "south": "RESERVOIR"},
        objects=[],
        flags=["water"],
        action=None
    ),
]
    # --- Begin: Unique rooms from act1.mud and act2.mud ---
rooms.extend([
        Room(
            id="BOOM-ROOM",
            desc_long="A room which reeks of coal gas. Dangerous to light anything here.",
            desc_short="Coal gas room.",
            exits={},
            objects=[GameObject("candle", "A wax candle."), GameObject("torch", "A wooden torch."), GameObject("match", "A matchstick.")]
        ),
        Room(
            id="BATS-ROOM",
            desc_long="You are in a small room which has only one door, to the east. A deranged vampire bat may be present.",
            desc_short="Bat room.",
            exits={"east": "BATS-EAST-ROOM"},
            objects=[GameObject("vampire bat", "A deranged vampire bat."), GameObject("garlic", "A clove of garlic.")]
        ),
        Room(
            id="MACHINE-ROOM",
            desc_long="A room with a machine. The machine may be open or closed.",
            desc_short="Machine room.",
            exits={},
            objects=[GameObject("machine", "A complex machine."), GameObject("coal", "A lump of coal."), GameObject("screw", "A metal screw.")]
        ),
        Room(
            id="FALLS-ROOM",
            desc_long="You are at the top of Aragain Falls, an enormous waterfall with a drop of about 450 feet. The only path here is on the north end.",
            desc_short="Top of Aragain Falls.",
            exits={"north": "FALLS-NORTH-ROOM"},
            objects=[GameObject("rainbow", "A beautiful rainbow (may be solid)."), GameObject("falls", "The Aragain Falls.")]
        ),
    ])
    # --- End: Unique rooms from act1.mud and act2.mud ---
 # --- Begin: Rooms from act3.mud ---
rooms.extend([
        Room(
            id="MAGNET-ROOM",
            desc_long="You are in a room with a low ceiling which is circular in shape. There are exits to the east and the southeast.",
            desc_short="Circular magnet room.",
            exits={"east": "CMACH-ROOM", "southeast": "ALICE-ROOM"},
            objects=[GameObject("magnet", "A powerful magnet.")]
        ),
        Room(
            id="CMACH-ROOM",
            desc_long="A room with machinery. See CMACH-DESC for details.",
            desc_short="Machinery room.",
            exits={},
            objects=[GameObject("machinery", "Complex machinery.")]
        ),
        Room(
            id="CAGED-ROOM",
            desc_long="A room with a cage puzzle. Description changes if the cage is solved.",
            desc_short="Caged puzzle room.",
            exits={},
            objects=[GameObject("cage", "A sturdy cage."), GameObject("robot", "A mechanical robot.")]
        ),
        Room(
            id="BKBOX-ROOM",
            desc_long="Bank box room. Exits and objects depend on SCOL-ROOMS context.",
            desc_short="Bank box room.",
            exits={},
            objects=[GameObject("bank box", "A secure bank box.")]
        ),
        Room(
            id="TELLER-ROOM",
            desc_long="A teller room. Above an open door is a sign reading BANK PERSONNEL ONLY.",
            desc_short="Teller room.",
            exits={},
            objects=[GameObject("teller", "A bank teller.")]
        ),
        Room(
            id="TREE-ROOM",
            desc_long="You are in a tree. On the ground below you can see various objects.",
            desc_short="Tree room.",
            exits={"down": "FORE3-ROOM"},
            objects=[GameObject("tree", "A tall tree."), GameObject("nest", "A bird's nest."), GameObject("egg", "A mysterious egg.")]
        ),
        Room(
            id="FOREST-ROOM",
            desc_long="A forest room. You hear the chirping of a song bird in the distance.",
            desc_short="Forest room.",
            exits={},
            objects=[GameObject("songbird", "A distant songbird.")]
        ),
        Room(
            id="CPANT-ROOM",
            desc_long="This is a small square room, in the middle of which is a recently created hole. There are exits to the west and south.",
            desc_short="Puzzle antechamber.",
            exits={"west": "CPWEST-ROOM", "south": "CPSOUTH-ROOM"},
            objects=[GameObject("ladder", "A sturdy ladder.")]
        ),
        Room(
            id="CP-ROOM",
            desc_long="Small square room bounded to the north and west with marble walls and to the east and south with sandstone walls.",
            desc_short="Puzzle room.",
            exits={},
            objects=[GameObject("puzzle", "A complex puzzle.")]
        ),
        Room(
            id="CPOUT-ROOM",
            desc_long="You are in a room with an exit to the north and a passage or metal door to the east.",
            desc_short="Puzzle exit room.",
            exits={"north": "CPNORTH-ROOM", "east": "CPEAST-ROOM"},
            objects=[GameObject("door", "A metal door."), GameObject("passage", "A dark passage.")]
        ),
        Room(
            id="PRM-ROOM",
            desc_long="This is a tiny room, which has an exit to the east.",
            desc_short="Tiny puzzle room.",
            exits={"east": "PREAST-ROOM"},
            objects=[GameObject("door", "A small door."), GameObject("keyhole", "A tiny keyhole.")]
        ),
        Room(
            id="PALANTIR-ROOM",
            desc_long="A room with a palantir puzzle. Door to the south.",
            desc_short="Palantir room.",
            exits={"south": "PALANTIR-SOUTH-ROOM"},
            objects=[GameObject("palantir", "A mysterious palantir.")]
        ),
        Room(
            id="SLIDE-ROOM",
            desc_long="A slide room. A timber tie is lying on the ground here. Tied to it is a piece of rope, which is dangling down the slide.",
            desc_short="Slide room.",
            exits={"down": "CELLA-ROOM"},
            objects=[GameObject("timber tie", "A timber tie."), GameObject("rope", "A dangling rope.")]
        ),
        Room(
            id="SLEDG-ROOM",
            desc_long="Sledge puzzle room.",
            desc_short="Sledge room.",
            exits={},
            objects=[GameObject("sledge", "A heavy sledge.")]
        ),
    ])
 # --- End: Rooms from act3.mud ---

 # --- Begin: Rooms from act4.mud ---
rooms.extend([
        Room(
            id="TOMB-ROOM",
            desc_long="A room with a tomb. The tomb can be open or closed.",
            desc_short="Tomb room.",
            exits={},
            objects=[GameObject("tomb", "An ancient tomb.")]
        ),
        Room(
            id="CRYPT-ROOM",
            desc_long="A room with a crypt. The crypt can be open or closed.",
            desc_short="Crypt room.",
            exits={},
            objects=[GameObject("crypt", "A stone crypt.")]
        ),
        Room(
            id="ENDGAME-START-ROOM",
            desc_long="Endgame start room, reached from the crypt.",
            desc_short="Endgame start.",
            exits={"south": "TSTRS-ROOM"},
            objects=[GameObject("lamp", "A brass lamp."), GameObject("sword", "A gleaming sword.")]
        ),
        Room(
            id="MIRROR-ROOM-ENDGAME",
            desc_long="A narrow room with a large mirror or wooden panel on one wall, and solid rock on the opposite wall.",
            desc_short="Mirror room (endgame).",
            exits={},
            objects=[GameObject("mirror", "A large mirror."), GameObject("panel", "A wooden panel."), GameObject("button", "A small button."), GameObject("pole", "A long pole.")]
        ),
        Room(
            id="MREYE-ROOM",
            desc_long="You are in a small room, with narrow passages exiting to the north and south. A narrow red beam of light crosses the room at the north end, inches above the floor.",
            desc_short="Mirror eye room.",
            exits={"north": "MREYE-NORTH-ROOM", "south": "MREYE-SOUTH-ROOM"},
            objects=[GameObject("beam", "A red beam of light.")]
        ),
        Room(
            id="MAGIC-MIRROR-ROOM",
            desc_long="Room with a pole and mirror structure. Description depends on pole and mirror state.",
            desc_short="Magic mirror room.",
            exits={},
            objects=[GameObject("pole", "A movable pole."), GameObject("mirror", "A magic mirror.")]
        ),
    ])
 # --- End: Rooms from act4.mud ---



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
        if not self.current_room or self.current_room not in self.rooms:
            print("No valid current room.")
            return
        room = self.rooms[self.current_room]
        print(f"\n{room.id}\n{room.desc_long}")
        print("Exits: " + ", ".join(room.exits.keys()))

    def move(self, direction):
        if not self.current_room or self.current_room not in self.rooms:
            print("No valid current room.")
            return
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
