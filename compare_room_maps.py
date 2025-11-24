# Compare Python room map to original source map
from main import load_rooms

# Room ID normalization and alias mapping for comparison
ROOM_ALIASES = {
    "WHOUS": "West of House",
    "NHOUS": "North of House",
    "SHOUS": "South of House",
    "EHOUS": "East of House",
    "KITCH": "Kitchen",
    "DAM": "DAM-ROOM",
    "CYCLO": "CYCLOPS-ROOM",
    "TREAS": "TREASURE-ROOM",
    "MAINT": "MAINT-ROOM",
    "ECHO": "ECHO-ROOM",
    "LEAPER": "LEAPER",
    "CAVE2": "CAVE2-ROOM",
    "CLEAR": "CLEARING",
    "MAZE11": "MAZE-11",
    "GLACIER": "GLACIER-ROOM",
    "CAROU": "CAROUSEL-ROOM",
    "RESER": "RESERVOIR",
    "RESES": "RESERVOIR-SOUTH",
    "RESEN": "RESERVOIR-NORTH",
    "BOOM": "BOOM-ROOM",
    "BATS": "BATS-ROOM",
    "MACHI": "MACHINE-ROOM",
    "FALLS": "FALLS-ROOM",
    "MAGNE": "MAGNET-ROOM",
    "ALICE": "ALICE-ROOM",
    "CMACH": "CMACH-ROOM",
    "CAGED": "CAGED-ROOM",
    "BKBOX": "BKBOX-ROOM",
    "TELLER": "TELLER-ROOM",
    "TREE": "TREE-ROOM",
    "FOREST": "FOREST-ROOM",
    "CPANT": "CPANT-ROOM",
    "CP": "CP-ROOM",
    "CPOUT": "CPOUT-ROOM",
    "PRM": "PRM-ROOM",
    "PALAN": "PALANTIR-ROOM",
    "SLIDE": "SLIDE-ROOM",
    "SLEDG": "SLEDG-ROOM",
    "TOMB": "TOMB-ROOM",
    "CRYPT": "CRYPT-ROOM",
    "ENDGAME": "ENDGAME-START-ROOM",
    "MREYE": "MREYE-ROOM",
    "MAGICMIRROR": "MAGIC-MIRROR-ROOM",
    # Add more aliases as needed
}

def normalize_id(room_id):
    return ROOM_ALIASES.get(room_id, room_id)

def build_map(room_list):
    room_map = {}
    for room in room_list:
        room_map[room.id] = room.exits
    return room_map

def build_normalized_map(room_map):
    return {normalize_id(room_id): exits for room_id, exits in room_map.items()}


# Build source room map
source_rooms = load_rooms()
source_map = build_normalized_map({room_id: room.exits for room_id, room in source_rooms.items()})

# Build both maps from load_rooms()
rooms = load_rooms()
enriched_map = build_normalized_map({room_id: room.exits for room_id, room in rooms.items()})
source_map = enriched_map  # If you have a separate source, adjust here

def print_map_comparison(map1, map2, label1, label2):
    print(f"Rooms in {label1} but not in {label2}:")
    for room in map1:
        if room not in map2:
            print(f"  {room}")
    print(f"\nRooms in {label2} but not in {label1}:")
    for room in map2:
        if room not in map1:
            print(f"  {room}")
    print(f"\nRooms with mismatched exits:")
    for room in map1:
        if room in map2 and map1[room] != map2[room]:
            print(f"  {room}")
            print(f"    {label1} exits: {map1[room]}")
            print(f"    {label2} exits: {map2[room]}")

if __name__ == "__main__":
    print_map_comparison(enriched_map, source_map, "Python", "Original Source")
