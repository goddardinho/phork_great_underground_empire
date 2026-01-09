from main import Room
from entities import Room as RoomFlags

# Auto-generated room definitions from map.json

# Canonical room flag mapping (expand as needed)
CANONICAL_ROOM_FLAGS = {
    # Outdoors
    "WHOUS": RoomFlags.ROOM_OUTDOORS,
    "FOREST-ROOM": RoomFlags.ROOM_OUTDOORS,
    "CLEARING": RoomFlags.ROOM_OUTDOORS,
    "GARDEN": RoomFlags.ROOM_OUTDOORS,
    "YARD": RoomFlags.ROOM_OUTDOORS,
    "MEADOW": RoomFlags.ROOM_OUTDOORS,
    "HILL": RoomFlags.ROOM_OUTDOORS,
    "MOUNTAIN": RoomFlags.ROOM_OUTDOORS,
    "SHORE": RoomFlags.ROOM_OUTDOORS,
    "BEACH": RoomFlags.ROOM_OUTDOORS,
    # Water
    "DAM-ROOM": RoomFlags.ROOM_WATER,
    "RESERVOIR": RoomFlags.ROOM_WATER,
    "RESERVOIR-SOUTH": RoomFlags.ROOM_WATER,
    "RESERVOIR-NORTH": RoomFlags.ROOM_WATER,
    "FALLS-ROOM": RoomFlags.ROOM_WATER,
    "RIVER": RoomFlags.ROOM_WATER,
    "POOL": RoomFlags.ROOM_WATER,
    "POND": RoomFlags.ROOM_WATER,
    # Dark
    "CELLAR": RoomFlags.ROOM_DARK,
    "CYCLOPS-ROOM": RoomFlags.ROOM_DARK | RoomFlags.ROOM_DEADLY,
    "MAZE-11": RoomFlags.ROOM_DARK,
    "GRUE-FUNCTION": RoomFlags.ROOM_DARK | RoomFlags.ROOM_DEADLY,
    "DOME-ROOM": RoomFlags.ROOM_DARK,
    "TOMB-FUNCTION": RoomFlags.ROOM_DARK,
    # Deadly
    "TROLL": RoomFlags.ROOM_DEADLY,
    "GRUE-FUNCTION": RoomFlags.ROOM_DEADLY | RoomFlags.ROOM_DARK,
    "CYCLOPS-ROOM": RoomFlags.ROOM_DEADLY | RoomFlags.ROOM_DARK,
    # Magic
    "TREAS": RoomFlags.ROOM_MAGIC,
    "MAGNET-ROOM": RoomFlags.ROOM_MAGIC,
    "MIRROR-ROOM": RoomFlags.ROOM_MAGIC,
    "CAROUSEL-ROOM": RoomFlags.ROOM_MAGIC,
    # Sound
    "ECHO-ROOM": RoomFlags.ROOM_SOUND,
    # Locked
    "HOUSE": RoomFlags.ROOM_LOCKED,
    "LOCKED-DOOR": RoomFlags.ROOM_LOCKED,
    "CELL-DOOR": RoomFlags.ROOM_LOCKED,
    "SAFE-ROOM": RoomFlags.ROOM_LOCKED,
    # Add more as needed...
}
def forest_room_action(game, verb=None):
    # Canonical Zork FOREST-ROOM action logic
    # Handles 'GO-IN' (entering), 'C-INT' (clock interrupt), and default (bird sound)
    if verb == "GO-IN":
        # Enable bird event (stub)
        # In Zork, this would enable a clock event for the bird
        # Here, we just print a message for now
        print("You hear the distant chirping of a songbird.")
    elif verb == "C-INT":
        # 10% chance to hear a bird
        import random
        if random.random() < 0.1:
            print("You hear in the distance the chirping of a song bird.")
    # else: no-op for other verbs

def create_rooms():
    rooms = {}
    # Canonical forest room names from Zork source
    forest_rooms = [
        "FORE1", "FORE2", "FORE3", "FORE4", "FORE5", "CLEAR", "TREE"
    ]
    room_names = [
        # ...existing room names...
        "EGYPT", "LLD1", "FCHMP"
    ]

# Canonical Zork room action stubs (moved to module level for import/testing)
def kitchen_action(game, verb=None):
    if verb == "LOOK":
        print("[KITCHEN] You see the kitchen and the window state.")
    elif verb == "GO-IN":
        print("[KITCHEN] (Stub) Entering kitchen may trigger a clock event.")

def living_room_action(game, verb=None):
    if verb == "LOOK":
        print("[LIVING-ROOM] You see the living room, rug, and trap-door state.")
    elif verb == "TAKE":
        print("[LIVING-ROOM] (Stub) Taking from the trophy case.")
    elif verb == "PUT":
        print("[LIVING-ROOM] (Stub) Putting into the trophy case.")

def echo_room_action(game, verb=None, text=None):
    if verb == "LOOK":
        print("[ECHO-ROOM] You see the echo room.")
    elif verb == "BUG":
        print("Feature")
    elif verb == "FEATU":
        print("That's right.")
    elif text and "ECHO" in text.upper():
        print("The acoustics of the room change subtly.")

def mirror_room_action(game, verb=None):
    if verb == "LOOK":
        print("[MIRROR-ROOM] You see the mirror room and mirror state.")
    elif verb in ("RUB", "EXAMI", "TAKE", "MUNG", "THROW", "POKE"):
        print(f"[MIRROR-ROOM] (Stub) Mirror verb: {verb}")

def maint_room_action(game, verb=None):
    if verb == "C-INT":
        print("[MAINT-ROOM] (Stub) Water level increases, flooding possible.")

def cyclops_room_action(game, verb=None):
    if verb == "LOOK":
        print("[CYCLOPS-ROOM] You see the cyclops and room state.")
    elif verb == "GO-IN":
        print("[CYCLOPS-ROOM] (Stub) Entering may enable a clock event.")

def treasure_room_action(game, verb=None):
    if verb == "GO-IN":
        print("[TREASURE-ROOM] (Stub) Thief may defend the room.")

def grue_function_action(game, verb=None):
    if verb == "EXAMI":
        print("[GRUE-FUNCTION] You examine the grue.")
    elif verb == "FIND":
        print("[GRUE-FUNCTION] You try to find the grue.")

def tomb_function_action(game, verb=None):
    if verb == "LOOK":
        print("[TOMB-FUNCTION] You see the tomb.")
