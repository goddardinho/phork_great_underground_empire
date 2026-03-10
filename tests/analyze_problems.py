#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path('.') / 'src'))

from world.world import World
from world.room_loader import ZorkRoomLoader

# Load world
world = World()
loader = ZorkRoomLoader(world)
loader.load_from_mud_files(Path('zork_mtl_source'))

# Get problematic rooms
problematic_rooms = []
for room_id, room in world.rooms.items():
    issues = []
    
    # Check name issues (same logic as audit script)
    name = room.name
    if (not name or name == room_id or 
        (name.isupper() and len(name) <= 5) or
        name in ['UP', 'DOWN', 'NORTH', 'SOUTH', 'EAST', 'WEST'] or
        (name.startswith('MAZ') and name[-1].isdigit()) or
        (name.startswith('DEAD') and name[-1].isdigit()) or
        (name.startswith('FORE') and name[-1].isdigit()) or
        (name.startswith('MINE') and name[-1].isdigit()) or
        (name.startswith('RIVR') and name[-1].isdigit())):
        issues.append('NAME')
        
    # Check description issues
    desc = room.description
    if (not desc or len(desc) < 5 or
        desc in ['UP', 'DOWN', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'TREE'] or
        (desc.isupper() and len(desc) < 20)):
        issues.append('DESC')
    
    if issues:
        problematic_rooms.append((room_id, name, desc[:40] + '...' if len(desc) > 40 else desc, issues))

print(f'Found {len(problematic_rooms)} problematic rooms:')
print(f"{'Room':<7} | {'Name':<15} | {'Description':<40} | Issues")
print("-" * 80)
for room_id, name, desc, issues in sorted(problematic_rooms):
    print(f'{room_id:<7} | {name:<15} | {desc:<40} | {",".join(issues)}')