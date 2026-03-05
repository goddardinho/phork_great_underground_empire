"""
Room Loader for Zork MDL Files

Integrates the MDL parser with our World and Room systems.
"""

from pathlib import Path
from typing import Dict, Set

# Handle imports for both module and script execution
try:
    from ..world.world import World
    from ..world.room import Room  
    from ..parsers.mdl_parser import MDLParser, RoomData
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from world.world import World
    from world.room import Room  
    from parsers.mdl_parser import MDLParser, RoomData


class ZorkRoomLoader:
    """Loads rooms from original Zork .mud files into our World system."""
    
    def __init__(self, world: World):
        self.world = world
        self.parser = MDLParser()
        
    def load_from_mud_files(self, mud_directory: Path) -> int:
        """
        Load all rooms from .mud files in the specified directory.
        Returns the number of rooms loaded.
        """
        print(f"Loading Zork rooms from {mud_directory}...")
        
        # Parse all .mud files
        room_data = self.parser.parse_directory(mud_directory)
        
        if not room_data:
            print("No rooms found in .mud files")
            return 0
        
        # Convert to our Room objects and add to world
        loaded_count = 0
        
        for room_id, data in room_data.items():
            try:
                room = self._convert_to_room(data)
                self.world.add_room(room)
                loaded_count += 1
            except Exception as e:
                print(f"Warning: Failed to load room {room_id}: {e}")
        
        print(f"Successfully loaded {loaded_count} rooms from {len(room_data)} parsed")
        
        # Validate exits point to existing rooms
        self._validate_exits()
        
        return loaded_count
    
    def _convert_to_room(self, data: RoomData) -> Room:
        """Convert RoomData to our Room object."""
        
        # Clean up description
        description = data.long_description
        if description:
            # Remove extra whitespace and format nicely
            description = ' '.join(description.split())
        else:
            description = f"You are in {data.short_name}."
        
        # Filter exits to only include those that point to valid rooms
        # We'll validate these exist later  
        exits = {}
        for direction, target_room in data.exits.items():
            # Convert direction names to our standard format
            std_direction = self._standardize_direction(direction)
            if std_direction:
                # Resolve context-dependent connections
                if target_room == "KITCHEN-WINDOW-MARKER":
                    # KITCHEN-WINDOW is bidirectional: KITCH <-> EHOUS
                    if data.id == "EHOUS":
                        resolved_target = "KITCH"
                    elif data.id == "KITCH":
                        resolved_target = "EHOUS"  
                    else:
                        # Unexpected room with kitchen window - skip
                        continue
                    exits[std_direction] = resolved_target
                else:
                    exits[std_direction] = target_room
        
        return Room(
            id=data.id,
            name=data.short_name or data.id,
            description=description,
            exits=exits
        )
    
    def _standardize_direction(self, direction: str) -> str:
        """Convert MDL directions to our standard direction names."""
        
        direction = direction.lower().strip()
        
        # Map MDL directions to our standard ones
        direction_map = {
            'north': 'north',
            'south': 'south', 
            'east': 'east',
            'west': 'west',
            'northeast': 'northeast',
            'northwest': 'northwest',
            'southeast': 'southeast',
            'southwest': 'southwest',
            'up': 'up',
            'down': 'down',
            'enter': 'enter',
            'exit': 'exit',
            'out': 'out',
            'in': 'in'
        }
        
        return direction_map.get(direction, direction)
    
    def _validate_exits(self):
        """Validate that all room exits point to rooms that exist in the world."""
        
        all_rooms = self.world.rooms
        invalid_exits = []
        
        for room_id, room in all_rooms.items():
            for direction, target_id in room.exits.items():
                if target_id not in all_rooms:
                    invalid_exits.append((room_id, direction, target_id))
        
        if invalid_exits:
            print(f"Warning: Found {len(invalid_exits)} invalid exits:")
            for room_id, direction, target_id in invalid_exits[:10]:  # Show first 10
                print(f"  {room_id} -> {direction} -> {target_id} (room not found)")
            if len(invalid_exits) > 10:
                print(f"  ... and {len(invalid_exits) - 10} more")
        else:
            print("✓ All room exits validated successfully")


def test_room_loading():
    """Test function to verify room loading works."""
    
    print("=== Zork Room Loader Test ===")
    print()
    
    # Create world and loader
    world = World()
    loader = ZorkRoomLoader(world)
    
    # Load rooms from .mud files
    mud_dir = Path("zork_mtl_source")
    
    if not mud_dir.exists():
        print(f"Error: {mud_dir} directory not found")
        return
    
    room_count = loader.load_from_mud_files(mud_dir)
    
    print(f"\n=== Results ===")
    print(f"Loaded {room_count} rooms into world")
    print(f"World now contains {len(world.rooms)} rooms total")
    
    # Show some example rooms
    print(f"\nExample rooms:")
    example_ids = ['WHOUS', 'NHOUS', 'SHOUS', 'EHOUS', 'KITCH']
    
    for room_id in example_ids:
        room = world.get_room(room_id)
        if room:
            print(f"\n{room_id}: {room.name}")
            print(f"  Description: {room.description[:80]}...")
            print(f"  Exits: {list(room.exits.keys())}")
    
    print(f"\n✓ Room loading test complete!")


if __name__ == "__main__":
    test_room_loading()