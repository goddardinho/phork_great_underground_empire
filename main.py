
from entities import GameObject, Room, Player, Action
from parsers import parse_exits, parse_objects, parse_flags, parse_action
from typing import Optional, List, Dict
import re

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
