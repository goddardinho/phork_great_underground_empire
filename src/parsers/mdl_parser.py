"""
MDL File Parser for Zork Room Definitions

Parses original Zork .mud files (MDL format) to extract room data.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RoomData:
    """Represents parsed room data from MDL format."""
    
    id: str
    long_description: str
    short_name: str
    exits: Dict[str, str]  # direction -> room_id
    objects: List[str]     # object IDs
    flags: List[str]       # room flags
    action: Optional[str] = None
    
    
class MDLParser:
    """Parser for MDL (.mud) files containing Zork room definitions."""
    
    def __init__(self):
        self.rooms: Dict[str, RoomData] = {}
        
    def parse_room_block(self, text: str, start_pos: int) -> Tuple[Optional[RoomData], int]:
        """
        Parse a single <ROOM ...> block starting at start_pos.
        Returns (RoomData, end_position) or (None, start_pos) if no room found.
        """
        # Find room start pattern
        room_match = re.search(r'<ROOM\s+"([^"]+)"', text[start_pos:])
        if not room_match:
            return None, start_pos
            
        room_id = room_match.group(1)
        room_start = start_pos + room_match.start()
        
        # Find the end of this room definition (next <ROOM or <SETG or end of content)
        remaining_text = text[room_start:]
        
        # Look for the closing > that ends the room definition
        # This is complex because of nested structures
        bracket_count = 0
        pos = remaining_text.find('<ROOM')
        pos = remaining_text.find('>', pos)  # Skip the opening <ROOM
        pos += 1
        
        while pos < len(remaining_text):
            char = remaining_text[pos]
            if char == '<':
                bracket_count += 1
            elif char == '>':
                if bracket_count == 0:
                    # This is the closing bracket of our room
                    break
                bracket_count -= 1
            pos += 1
        
        room_text = remaining_text[:pos + 1]
        
        try:
            room_data = self._parse_room_content(room_id, room_text)
            return room_data, room_start + pos + 1
        except Exception as e:
            print(f"Warning: Failed to parse room {room_id}: {e}")
            return None, room_start + pos + 1
    
    def _parse_room_content(self, room_id: str, room_text: str) -> RoomData:
        """Parse the content within a room definition."""
        
        # Extract long description (first quoted string after room ID)
        desc_match = re.search(r'<ROOM\s+"[^"]+"\s*\n"([^"]*(?:\n[^"]*)*)"', room_text, re.MULTILINE | re.DOTALL)
        long_description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract short name (second quoted string)
        # Look for the pattern after the long description
        if desc_match:
            after_desc = room_text[desc_match.end():]
            # Look for next quoted string that's not part of EXIT
            name_match = re.search(r'^\s*"([^"]*)"(?!\s*")', after_desc, re.MULTILINE)
            short_name = name_match.group(1).strip() if name_match else room_id
        else:
            # Fallback: look for any quoted string after room ID
            name_match = re.search(r'<ROOM\s+"[^"]+"\s*"([^"]*)"', room_text)  
            short_name = name_match.group(1).strip() if name_match else room_id
        
        # If short name is empty or too long, use room_id or generate from description
        if not short_name or len(short_name) > 50:
            if long_description:
                # Try to extract a reasonable name from description
                if "west of" in long_description.lower():
                    short_name = "West of House" 
                elif "north of" in long_description.lower():
                    short_name = "North of House"
                elif "south of" in long_description.lower():
                    short_name = "South of House"
                elif "behind" in long_description.lower() and "house" in long_description.lower():
                    short_name = "Behind House"
                else:
                    # Use first few words of description as name
                    words = long_description.split()[:3]
                    short_name = " ".join(words).replace(",", "").replace(".", "")
            else:
                short_name = room_id
        
        # Extract exits from <EXIT ...> pattern
        exits = {}
        exit_match = re.search(r'<EXIT\s+([^>]*)>', room_text, re.DOTALL)
        if exit_match:
            exit_content = exit_match.group(1)
            # Parse direction-room pairs, ignoring #NEXIT entries which are blocked exits
            exit_pairs = re.findall(r'"([^"]+)"\s+"([^"#][^"]*)"', exit_content)
            for direction, target in exit_pairs:
                exits[direction.lower()] = target
        
        # Extract objects (items in parentheses)
        objects = []
        obj_match = re.search(r'\(\s*([^)]*)\s*\)', room_text)
        if obj_match:
            obj_content = obj_match.group(1).strip()
            if obj_content and obj_content != '<>':
                # Extract GET-OBJ references
                obj_refs = re.findall(r'<GET-OBJ\s+"([^"]+)">', obj_content)
                objects.extend(obj_refs)
        
        # Extract flags (simplified - just collect identifiers)
        flags = []
        flag_patterns = re.findall(r'R[A-Z]+BIT', room_text)
        flags.extend(flag_patterns)
        
        return RoomData(
            id=room_id,
            long_description=long_description,
            short_name=short_name,
            exits=exits,
            objects=objects,
            flags=flags
        )
    
    def parse_file(self, file_path: Path) -> Dict[str, RoomData]:
        """Parse an entire .mud file and extract all room definitions."""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {}
        
        rooms = {}
        pos = 0
        
        while pos < len(content):
            room_data, new_pos = self.parse_room_block(content, pos)
            
            if room_data:
                rooms[room_data.id] = room_data
                print(f"Parsed room: {room_data.id} - {room_data.short_name}")
            
            # Advance position
            if new_pos <= pos:
                pos += 1  # Prevent infinite loop
            else:
                pos = new_pos
        
        return rooms
    
    def parse_directory(self, directory_path: Path) -> Dict[str, RoomData]:
        """Parse all .mud files in a directory."""
        
        all_rooms = {}
        
        for mud_file in directory_path.glob("*.mud"):
            print(f"Parsing {mud_file.name}...")
            file_rooms = self.parse_file(mud_file)
            all_rooms.update(file_rooms)
        
        return all_rooms


def main():
    """Test the parser on the zork_mtl_source files."""
    
    parser = MDLParser()
    source_dir = Path("zork_mtl_source")
    
    if not source_dir.exists():
        print(f"Error: {source_dir} directory not found")
        return
    
    print("=== MDL Parser Test ===")
    print()
    
    rooms = parser.parse_directory(source_dir)
    
    print(f"\n=== Parsing Results ===")
    print(f"Found {len(rooms)} rooms total")
    
    # Show first few rooms as examples
    for i, (room_id, room_data) in enumerate(rooms.items()):
        if i >= 5:  # Just show first 5
            break
        print(f"\nRoom: {room_id}")
        print(f"  Name: {room_data.short_name}")
        print(f"  Description: {room_data.long_description[:60]}...")
        print(f"  Exits: {list(room_data.exits.keys())}")
        print(f"  Objects: {room_data.objects}")
    
    if len(rooms) > 5:
        print(f"\n... and {len(rooms) - 5} more rooms")


if __name__ == "__main__":
    main()