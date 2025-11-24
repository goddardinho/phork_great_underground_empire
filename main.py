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
        desc_long=(
            "A room with a large mirror. "
            "{mirror_state} "
            "There is an ugly person staring back at you, or the mirror is shattered."
        ),
        desc_short="A room with a large mirror.",
        exits={
            "east": "ECHO-ROOM"  # Conditional: only if mirror is intact
        },
        objects=[
            GameObject("mirror", "A large mirror, possibly broken.", attributes={"state": "intact", "breakable": True, "reflects": True, "can_shatter": True})
        ],
        flags=["reflective"],
        action=None
    ),
    Room(
        id="TORCH-ROOM",
        desc_long=(
            "A room with a torch. "
            "{torch_state} "
            "A large piece of rope descends from the railing above, ending some five feet above your head."
        ),
        desc_short="Torch room with rope.",
        exits={
            "up": "DOME-ROOM"  # Conditional: only if torch is lit
        },
        objects=[
            GameObject("torch", "A burning torch or an unlit torch.", attributes={"lit": False, "flammable": True, "can_light": True}),
            GameObject("rope", "A rope hanging from the railing.", attributes={"climbable": True, "tied": True, "can_untie": True})
        ],
        flags=["torch"],
        action=None
    ),
    Room(
        id="DOME-ROOM",
        desc_long="A dome-shaped room. Hanging down from the railing is a rope which ends about ten feet from the floor below. Jumping may be dangerous here.",
        desc_short="Dome room with rope.",
        exits={
            "south": "RESERVOIR-SOUTH"  # Conditional: only if bubble is glowing
        },
        objects=[GameObject("rope", "A rope hanging from the railing.")]
    ),
    Room(
        id="LLD2-ROOM",
        desc_long="A room in the Land of the Dead. If you are on the pole, you see a different description.",
        desc_short="Land of the Dead (2).",
        exits={},
        objects=[GameObject("pole", "A mysterious pole.", attributes={"interactable": True, "can_climb": True, "can_descend": True})]
    ),
    Room(
        id="DAM-ROOM",
        desc_long=(
            "Flood Control Dam #3. There is a control panel here, a large metal bolt, and a small green plastic bubble. "
            "{bubble_state} "
        ),
        desc_short="Flood Control Dam #3.",
        exits={},
        objects=[
            GameObject("control panel", "A dam control panel.", attributes={"interactive": True}),
            GameObject("metal bolt", "A large metal bolt.", attributes={"removable": True}),
            GameObject("green bubble", "A small green plastic bubble, possibly glowing.", attributes={"glowing": False})
        ],
        flags=["dam"],
        action=None
    ),
    Room(
        id="CYCLOPS-ROOM",
        desc_long=(
            "This room has an exit on the west side, and a staircase leading up. "
            "{cyclops_state} "
            "There may be a hole in the north wall depending on game state."
        ),
        desc_short="Cyclops room with stairs.",
        exits={
            "west": "CYCLOPS-WEST-ROOM",  # Conditional: only if cyclops is not hostile
            "up": "CYCLOPS-UP-STAIRS"     # Conditional: only if cyclops is awake
        },
        objects=[
            GameObject("cyclops", "A sleeping, angry, or absent cyclops.", attributes={"awake": False, "hostile": False, "movable": False})
        ],
        flags=["cyclops"],
        action=None
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
        desc_long="Maintenance room. The water level here may change. The toolbox may contain useful tools.",
        desc_short="Maintenance room.",
        exits={"east": "DAM-ROOM"},
        objects=[
            GameObject("toolbox", "A rusty toolbox.", attributes={"openable": True, "contains": ["wrench", "screwdriver"]}),
            GameObject("wrench", "A heavy wrench.", attributes={"usable": True}),
            GameObject("screwdriver", "A flathead screwdriver.", attributes={"usable": True})
        ],
        flags=["maintenance", "tools"],
        action="check_water_level"
    ),
    Room(
        id="ECHO-ROOM",
        desc_long="A room with strange acoustics. Sounds echo and may reveal hidden passages.",
        desc_short="A room with strange acoustics.",
        exits={"north": "MAZE-11", "south": "CAVE2-ROOM"},
        objects=[GameObject("echo", "A mysterious echo that repeats your words.", attributes={"reveals": "hidden passage"})],
        flags=["echo", "acoustics"],
        action="listen_for_echo"
    ),
    Room(
        id="LEAPER",
        desc_long="A room where you may need to jump. The ledge may be reachable if you jump high enough.",
        desc_short="A room for jumping.",
        exits={"up": "DOME-ROOM"},
        objects=[
            GameObject("ledge", "A narrow ledge.", attributes={"reachable": False}),
            GameObject("floor", "A stone floor.", attributes={"jumpable": True})
        ],
        flags=["jump", "challenge"],
        action="attempt_jump"
    ),
    Room(
        id="CAVE2-ROOM",
        desc_long="A windy cave. Your candles may blow out here. The wind may reveal hidden items.",
        desc_short="A windy cave.",
        exits={"west": "ECHO-ROOM"},
        objects=[
            GameObject("candle", "A candle, possibly blown out.", attributes={"lit": False, "blowable": True, "can_light": True}),
            GameObject("wind", "A strong wind.", attributes={"reveals": "hidden item", "can_extinguish": True})
        ],
        flags=["windy", "dark"],
        action="search_wind"
    ),
    Room(
        id="CLEARING",
        desc_long="You are in a clearing, with a forest surrounding you on the west and south. There is a grating here. The grating may be locked or open.",
        desc_short="You are in a clearing, with a forest surrounding you on the west and south. There is a grating here.",
        exits={"north": "FOREST", "east": "HOUSE"},
        objects=[GameObject("grating", "A metal grating.", attributes={"locked": True, "openable": True, "can_unlock": True, "can_open": True})],
        flags=["outdoors", "entry"],
        action="open_grating"
    ),
    Room(
        id="MAZE-11",
        desc_long="You are in a small room near the maze. There are twisty passages in the immediate vicinity. Above you is a grating. The maze may shift as you move.",
        desc_short="You are in a small room near the maze. There are twisty passages in the immediate vicinity. Above you is a grating.",
        exits={"south": "ECHO-ROOM"},
        objects=[
            GameObject("grating", "A metal grating above.", attributes={"locked": False, "openable": True}),
            GameObject("maze", "A shifting maze.", attributes={"shifts": True})
        ],
        flags=["maze", "shifting"],
        action="navigate_maze"
    ),
    Room(
        id="GLACIER-ROOM",
        desc_long="A glacier blocks your way. There is a large passageway leading westward. Part of the glacier may be melted.",
        desc_short="A glacier blocks your way. There is a large passageway leading westward. Part of the glacier may be melted.",
        exits={"west": "CAVE2-ROOM"},
        objects=[
            GameObject("glacier", "A massive glacier.", attributes={"meltable": True, "blocks_path": True}),
            GameObject("ice", "A chunk of ice.", attributes={"cold": True, "can_pickup": True})
        ],
        flags=["cold", "ice"],
        action="melt_glacier"
    ),
    Room(
        id="CAROUSEL-ROOM",
        desc_long="You are in a circular room with passages off in eight directions. Your compass needle spins wildly, and you can't get your bearings.",
        desc_short="You are in a circular room with passages off in eight directions. Your compass needle spins wildly, and you can't get your bearings.",
        exits={"north": "MAZE-11", "south": "GLACIER-ROOM"},
        objects=[
            GameObject("compass", "A spinning compass needle.", attributes={"spinning": True, "can_stop": True}),
            GameObject("door", "A mysterious door.", attributes={"locked": True, "can_unlock": True})
        ],
        flags=["carousel", "confusion"],
        action="stop_compass"
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
        objects=[
            GameObject("mud", "A large mud pile.", attributes={"sticky": True, "can_sink": True}),
            GameObject("shore", "A muddy shore.", attributes={"walkable": True}),
            GameObject("puddle", "A small puddle of water.", attributes={"wet": True, "can_dry": True})
        ],
        flags=["water", "mud"],
        action="cross_mud"
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
            objects=[
                GameObject("vampire bat", "A deranged vampire bat.", attributes={"hostile": True, "can_flee": True}),
                GameObject("garlic", "A clove of garlic.", attributes={"repels_bat": True})
            ],
            flags=["bat", "danger"],
            action="repel_bat"
        ),
        Room(
            id="MACHINE-ROOM",
            desc_long="A room with a machine. The machine may be open or closed.",
            desc_short="Machine room.",
            exits={},
            objects=[
                GameObject("machine", "A complex machine.", attributes={"openable": True, "can_operate": True}),
                GameObject("coal", "A lump of coal.", attributes={"burnable": True}),
                GameObject("screw", "A metal screw.", attributes={"can_unscrew": True})
            ],
            flags=["machine", "mechanical"],
            action="operate_machine"
        ),
        Room(
            id="FALLS-ROOM",
            desc_long="You are at the top of Aragain Falls, an enormous waterfall with a drop of about 450 feet. The only path here is on the north end.",
            desc_short="Top of Aragain Falls.",
            exits={"north": "FALLS-NORTH-ROOM"},
            objects=[
                GameObject("rainbow", "A beautiful rainbow (may be solid).", attributes={"solid": False, "can_cross": True}),
                GameObject("falls", "The Aragain Falls.", attributes={"dangerous": True, "can_fall": True})
            ],
            flags=["waterfall", "danger"],
            action="cross_rainbow"
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
            objects=[
                GameObject("magnet", "A powerful magnet.", attributes={"magnetic": True, "can_attract": True}),
                GameObject("nail", "A metal nail.", attributes={"attractable": True})
            ],
            flags=["magnet", "circular"],
            action="use_magnet"
        ),
        Room(
            id="ALICE-ROOM",
            desc_long="A whimsical room with shifting walls and a sense of unreality. The southeast wall seems to shimmer, and objects may appear or vanish unexpectedly.",
            desc_short="Whimsical, shifting room.",
            exits={"north": "MAGNET-ROOM", "west": "CAGED-ROOM"},
            objects=[
                GameObject("chess piece", "A mysterious chess piece, possibly alive.", attributes={"movable": True, "can_transform": True}),
                GameObject("mirror", "A small hand mirror.", attributes={"reflective": True, "can_shatter": True})
            ],
            flags=["whimsical", "illusion", "dynamic"],
            action="shift_walls"
        ),
        Room(
            id="CMACH-ROOM",
            desc_long="A room with machinery. See CMACH-DESC for details.",
            desc_short="Machinery room.",
            exits={},
            objects=[
                GameObject("machinery", "Complex machinery.", attributes={"operable": True, "can_break": True}),
                GameObject("gear", "A large gear.", attributes={"can_turn": True})
            ],
            flags=["machinery", "mechanical"],
            action="operate_machinery"
        ),
        Room(
            id="CAGED-ROOM",
            desc_long="A room with a cage puzzle. Description changes if the cage is solved.",
            desc_short="Caged puzzle room.",
            exits={},
            objects=[
                GameObject("cage", "A sturdy cage.", attributes={"locked": True, "can_unlock": True}),
                GameObject("robot", "A mechanical robot.", attributes={"programmable": True, "can_escape": True})
            ],
            flags=["cage", "puzzle"],
            action="solve_cage_puzzle"
        ),
        Room(
            id="BKBOX-ROOM",
            desc_long="Bank box room. Exits and objects depend on SCOL-ROOMS context.",
            desc_short="Bank box room.",
            exits={},
            objects=[
                GameObject("bank box", "A secure bank box.", attributes={"locked": True, "can_open": True}),
                GameObject("key", "A small key.", attributes={"can_unlock": True})
            ],
            flags=["bank", "secure"],
            action="open_bank_box"
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
