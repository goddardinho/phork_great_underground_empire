from entities import Room, GameObject
from typing import Optional, List, Dict

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
    # ... (add the rest as needed) ...
}

# This is a placeholder for the actual room dictionary population logic
rooms_dict: Dict[str, Room] = {}

# You can add logic here to populate rooms_dict from source files or other means
