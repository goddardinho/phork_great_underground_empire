 # --- Begin: Rooms from act4.mud ---
# --- End: Rooms added from source comparison ---
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
# --- End: Rooms added from source comparison ---
rooms_dict = globals().get('rooms', None)
if isinstance(rooms_dict, dict):
    # Add remaining rooms from source with placeholder data
    for room_id in [
        "CANY1", "CHAS3", "CHAS2", "CHAS1", "MAZE1", "MAZE2", "MAZE3", "MAZE4", "MAZE5", "MAZE6", "MAZE7", "MAZE8", "MAZE9", "MAZ10", "MAZ11", "MGRAT", "MAZ12", "DEAD4", "MAZ13", "MAZ14", "MAZ15", "BLROO", "RAVI1", "CRAW1", "STREA", "INSTR", "EGYPT", "ICY", "RUBYR", "ATLAN", "MIRR1", "MIRR2", "CAVE1", "CRAW2", "CRAW3", "PASS3", "PASS4", "ENTRA", "SQUEE", "TSHAF", "TUNNE", "SMELL", "TLADD", "BLADD", "DEAD7", "TIMBE", "BSHAF", "MINE1", "MINE2", "MINE3", "MINE4", "MINE5", "MINE6", "MINE7", "DOME", "MTORC", "CRAW4", "PASS1", "PASS5", "CAVE3", "DEAD5", "DEAD6", "CAVE4", "RIDDL", "MPEAR", "LLD1", "LLD2", "MGRAI", "TEMP1", "TEMP2", "LOBBY", "DOCK", "RIVR1", "RIVR2", "RIVR3", "WCLF1", "WCLF2", "RIVR4", "RIVR5", "FCHMP", "FANTE", "BEACH", "RCAVE", "TCAVE", "RAINB", "POG", "CLBOT", "CLMID", "CLTOP", "VLBOT", "VAIR1", "VAIR2", "VAIR3", "VAIR4", "LEDG2", "LIBRA", "LEDG3", "LEDG4", "SAFE", "LAVA", "CAGER", "TWELL", "BWELL", "ALISM", "ALITR", "BKENT", "BKTW", "BKTE", "BKVW", "BKVE", "BKTWI", "BKVAU", "BKEXE", "SLID1", "SLID2", "SLID3", "SPAL", "MRD", "MRG", "MRC", "MRB", "MRA", "MRDE", "MRDW", "MRGE", "MRGW", "MRCE", "MRCW", "MRBE", "MRBW", "MRAE", "MRAW", "INMIR", "MRANT", "TSTRS", "ECORR", "WCORR", "SCORR", "BDOOR", "FDOOR", "NCORR", "PARAP", "CELL", "PCELL", "NCELL", "NIRVA", "OPTIONAL"
    ]:
        if room_id not in rooms_dict:
            rooms_dict[room_id] = Room(
                id=room_id,
                desc_long=f"Room {room_id} from source. Description not yet extracted.",
                desc_short=f"{room_id} (source)",
                exits={},
                objects=[]
            )



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
    import glob
    rooms = {}
    mud_files = glob.glob("zork_mtl_source/*.mud")
    room_id: Optional[str] = None
    desc_long: Optional[str] = None
    desc_short: Optional[str] = None
    exits: Dict[str, str] = {}
    objects: List[GameObject] = []
    flags: List[str] = []
    action: Optional[str] = None
    for mud_file in mud_files:
        try:
            with open(mud_file, "r") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith('<ROOM') or line.startswith('<DEFINE ROOM'):
                    if room_id:
                        room = Room(room_id, desc_long or "", desc_short or "", exits, objects, flags, action)
                        rooms[room_id] = room
                    parts = line.split('"')
                    room_id = parts[1] if len(parts) > 1 else None
                    desc_long = None
                    desc_short = None
                    exits = {}
                    aliases = {
                        "NHOUS": "North of House",
                        "WHOUS": "West of House",
                        "SHOUS": "South of House",
                        "EHOUS": "East of House",
                        "HOUSE": "West of House",
                        "KITCH": "Kitchen",
                        "KITC": "Kitchen",
                        "ATTIC": "ATTIC",
                        "LROOM": "LROOM",
                        "FORE1": "FORE1",
                        "FORE2": "FORE2",
                        "FORE3": "FORE3",
                        "FORE4": "FORE4",
                        "FORE5": "FORE5",
                        "CELLA": "CELLA",
                        "MTROL": "MTROL",
                        "STUDI": "STUDI",
                        "GALLE": "GALLE",
                        "CAVE2": "CAVE2-ROOM",
                        "ECHO": "ECHO-ROOM",
                        "DAM": "DAM-ROOM",
                        "MAINT": "MAINT-ROOM",
                        "TREAS": "TREASURE-ROOM",
                        "CYCLO": "CYCLOPS-ROOM",
                        "CYCLOPS": "CYCLOPS-ROOM",
                        "RESEN": "RESEN",
                        "RESERVOIR": "RESERVOIR",
                        "RESN": "RESERVOIR-NORTH",
                        "RESS": "RESERVOIR-SOUTH",
                        "CAROU": "CAROUSEL-ROOM",
                        "GLACIER": "GLACIER-ROOM",
                        "BOOM": "BOOM-ROOM",
                        "BATS": "BATS-ROOM",
                        "TELLER": "TELLER-ROOM",
                        "TREE": "TREE-ROOM",
                        "CPANT": "CPANT-ROOM",
                        "CP": "CP-ROOM",
                        "CPOUT": "CPOUT-ROOM",
                        "PRM": "PRM-ROOM",
                        "PALANTIR": "PALANTIR-ROOM",
                        "SLIDE": "SLIDE-ROOM",
                        "SLEDG": "SLEDG-ROOM",
                        "TOMB": "TOMB-ROOM",
                        "CRYPT": "CRYPT-ROOM",
                        "ENDGAME": "ENDGAME-START-ROOM",
                        "MIRREND": "MIRROR-ROOM-ENDGAME",
                        "MREYE": "MREYE-ROOM",
                        "MAGICMIR": "MAGIC-MIRROR-ROOM",
                        "CRAW4": "CRAW4",
                        "PASS1": "PASS1",
                        "PASS5": "PASS5",
                        "CAVE3": "CAVE3",
                        "DEAD5": "DEAD5",
                        "DEAD6": "DEAD6",
                        "CAVE4": "CAVE4",
                        "RIDDL": "RIDDL",
                        "MPEAR": "MPEAR",
                        "LLD1": "LLD1",
                        "LLD2": "LLD2",
                        "MGRAI": "MGRAI",
                        "TEMP1": "TEMP1",
                        "TEMP2": "TEMP2",
                        "LOBBY": "LOBBY",
                        "DOCK": "DOCK",
                        "RIVR1": "RIVR1",
                        "RIVR2": "RIVR2",
                        "RIVR3": "RIVR3",
                        "WCLF1": "WCLF1",
                        "WCLF2": "WCLF2",
                        "RIVR4": "RIVR4",
                        "RIVR5": "RIVR5",
                        "FCHMP": "FCHMP",
                        "FANTE": "FANTE",
                        "BEACH": "BEACH",
                        "RCAVE": "RCAVE",
                        "TCAVE": "TCAVE",
                        "RAINB": "RAINB",
                        "POG": "POG",
                        "CLBOT": "CLBOT",
                        "CLMID": "CLMID",
                        "CLTOP": "CLTOP",
                        "VLBOT": "VLBOT",
                        "VAIR1": "VAIR1",
                        "VAIR2": "VAIR2",
                        "VAIR3": "VAIR3",
                        "VAIR4": "VAIR4",
                        "LEDG2": "LEDG2",
                        "LIBRA": "LIBRA",
                        "LEDG3": "LEDG3",
                        "LEDG4": "LEDG4",
                        "SAFE": "SAFE",
                        "LAVA": "LAVA",
                        "CAGER": "CAGER",
                        "TWELL": "TWELL",
                        "BWELL": "BWELL",
                        "ALISM": "ALISM",
                        "ALITR": "ALITR",
                        "BKENT": "BKENT",
                        "BKTW": "BKTW",
                        "BKTE": "BKTE",
                        "BKVW": "BKVW",
                        "BKVE": "BKVE",
                        "BKTWI": "BKTWI",
                        "BKVAU": "BKVAU",
                        "BKEXE": "BKEXE",
                        "SLID1": "SLID1",
                        "SLID2": "SLID2",
                        "SLID3": "SLID3",
                        "SPAL": "SPAL",
                        "MRD": "MRD",
                        "MRG": "MRG",
                        "MRC": "MRC",
                        "MRB": "MRB",
                        "MRA": "MRA",
                        "MRDE": "MRDE",
                        "MRDW": "MRDW",
                        "MRGE": "MRGE",
                        "CANY1": "CANY1",
                        "CHAS3": "CHAS3",
                        "CHAS2": "CHAS2",
                        "CHAS1": "CHAS1",
                        "MAZE1": "MAZE1",
                        "MAZE2": "MAZE2",
                        "MAZE3": "MAZE3",
                        "MAZE4": "MAZE4",
                        "MAZE5": "MAZE5",
                        "MAZE6": "MAZE6",
                        "MAZE7": "MAZE7",
                        "MAZE8": "MAZE8",
                        "MAZE9": "MAZE9",
                        "MAZ10": "MAZ10",
                        "MAZ11": "MAZ11",
                        "MGRAT": "MGRAT",
                        "MAZ12": "MAZ12",
                        "DEAD4": "DEAD4",
                        "MAZ13": "MAZ13",
                        "MAZ14": "MAZ14",
                        "MAZ15": "MAZ15",
                        "BLROO": "BLROO",
                        "RAVI1": "RAVI1",
                        "CRAW1": "CRAW1",
                        "STREA": "STREA",
                        "INSTR": "INSTR",
                        "EGYPT": "EGYPT",
                        "ICY": "ICY",
                        "RUBYR": "RUBYR",
                        "ATLAN": "ATLAN",
                        "MIRR1": "MIRR1",
                        "MIRR2": "MIRR2",
                        "CAVE1": "CAVE1",
                        "CRAW2": "CRAW2",
                        "CRAW3": "CRAW3",
                        "PASS3": "PASS3",
                        "PASS4": "PASS4",
                        "ENTRA": "ENTRA",
                        "SQUEE": "SQUEE",
                        "TSHAF": "TSHAF",
                        "TUNNE": "TUNNE",
                        "SMELL": "SMELL",
                        "TLADD": "TLADD",
                        "BLADD": "BLADD",
                        "DEAD7": "DEAD7",
                        "TIMBE": "TIMBE",
                        "BSHAF": "BSHAF",
                        "MINE1": "MINE1",
                        "MINE2": "MINE2",
                        "MINE3": "MINE3",
                        "MINE4": "MINE4",
                        "MINE5": "MINE5",
                        "MINE6": "MINE6",
                        "MINE7": "MINE7",
                        "DOME": "DOME",
                        "MTORC": "MTORC",
                        "CRAW4": "CRAW4",
                        "PASS1": "PASS1",
                    }
                # Extract exits from <EXIT ...> blocks
                if line.startswith('<EXIT'):
                    # Find all direction/destination pairs
                    exit_pairs = re.findall(r'"([A-Z]+)"\s+(?:,)?"([A-Z0-9\-]+)"', line)
                    for direction, dest in exit_pairs:
                        # process exits here
                        pass
        except Exception as e:
            print(f"Error reading {mud_file}: {e}")
    return rooms
