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
        
        # Extract quoted strings in order - this handles the MDL room format properly
        quoted_strings = re.findall(r'"([^"]*)"', room_text)
        
        # MDL Room format: <ROOM "ID" "long_desc" "short_name" <EXIT ...> ...>
        long_description = ""
        short_name = room_id  # Default fallback
        
        if len(quoted_strings) >= 2:
            # First string after ID is long description (can be empty)
            long_description = quoted_strings[0].strip()
            
            # Second string is short name
            short_name = quoted_strings[1].strip()
            
            # If short name is empty, try to generate from long description or use fallback
            if not short_name:
                if long_description:
                    # Try to extract a reasonable name from description
                    if "west of" in long_description.lower() and "house" in long_description.lower():
                        short_name = "West of House"
                    elif "north of" in long_description.lower() and "house" in long_description.lower():
                        short_name = "North of House"
                    elif "south of" in long_description.lower() and "house" in long_description.lower():
                        short_name = "South of House"
                    elif "behind" in long_description.lower() and "house" in long_description.lower():
                        short_name = "Behind House"
                    elif "east of" in long_description.lower() and "house" in long_description.lower():
                        short_name = "East of House"
                    elif "kitchen" in long_description.lower():
                        short_name = "Kitchen"
                    elif "attic" in long_description.lower():
                        short_name = "Attic"
                    elif "living room" in long_description.lower():
                        short_name = "Living Room"
                    else:
                        # Use first few words of description as name
                        words = long_description.split()[:3]
                        short_name = " ".join(words).replace(",", "").replace(".", "")
                else:
                    short_name = room_id
        elif len(quoted_strings) >= 1:
            # Only one string - use as both description and name basis
            long_description = quoted_strings[0].strip()
            if long_description:
                # Use description to infer name
                if "west of" in long_description.lower():
                    short_name = "West of House"
                elif "north of" in long_description.lower():
                    short_name = "North of House"
                else:
                    words = long_description.split()[:3]
                    short_name = " ".join(words).replace(",", "").replace(".", "")
            else:
                short_name = room_id

        # If we still don't have a good name, try some common ID mappings
        if short_name == room_id:
            name_mappings = {
                "WHOUS": "West of House",
                "NHOUS": "North of House", 
                "SHOUS": "South of House",
                "EHOUS": "Behind House",  # Fixed: was "East of House", should be "Behind House" per .mud file
                "KITCH": "Kitchen",
                "ATTIC": "Attic",
                "LROOM": "Living Room",
                "CLEAR": "Clearing",
                "MGRAT": "Grating Room",
                "FORE1": "Forest Path",
                "FORE2": "Forest",
                "FORE3": "Forest",
                "FORE4": "Forest",
                "FORE5": "Forest",
            }
            short_name = name_mappings.get(room_id, room_id)

        # Extract exits from <EXIT ...> pattern
        exits = {}
        exit_match = re.search(r'<EXIT\s+([^>]*)>', room_text, re.DOTALL)
        if exit_match:
            exit_content = exit_match.group(1)
            exits = self._parse_exits(exit_content)
        
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
            long_description=short_name,  # Swap: was long_description
            short_name=long_description,  # Swap: was short_name
            exits=exits,
            objects=objects,
            flags=flags
        )

    def _parse_exits(self, exit_content: str) -> Dict[str, str]:
        """Parse complex exit structures from MDL format."""
        exits = {}
        
        # Remove newlines and multiple spaces for easier parsing
        exit_content = ' '.join(exit_content.split())
        
        # Split into individual direction-destination pairs
        # Handle quoted strings, DOOR structures, NEXIT, CEXIT, etc.
        i = 0
        while i < len(exit_content):
            # Skip whitespace
            while i < len(exit_content) and exit_content[i].isspace():
                i += 1
            
            if i >= len(exit_content):
                break
                
            # Look for direction (quoted string)
            if exit_content[i] == '"':
                direction, i = self._extract_quoted_string(exit_content, i)
                if not direction:
                    continue
                    
                # Skip whitespace after direction
                while i < len(exit_content) and exit_content[i].isspace():
                    i += 1
                    
                if i >= len(exit_content):
                    break
                
                # Parse the destination based on what follows
                destination = None
                
                if exit_content[i:].startswith('#NEXIT'):
                    # Blocked exit - skip this entirely
                    i = self._skip_nexit(exit_content, i)
                    continue
                elif exit_content[i] == '<':
                    # Complex structure (DOOR, CEXIT, etc.)
                    if exit_content[i:].startswith('<DOOR'):
                        destination, i = self._parse_door_structure(exit_content, i)
                    elif exit_content[i:].startswith('<CEXIT'):
                        destination, i = self._parse_cexit_structure(exit_content, i)
                    else:
                        # Unknown structure - skip it
                        i = self._skip_structure(exit_content, i)
                elif exit_content[i] == '"':
                    # Simple room name
                    destination, i = self._extract_quoted_string(exit_content, i)
                elif exit_content[i] == ',':
                    # Variable reference like ,MR-G - extract the variable name
                    destination, i = self._extract_variable_ref(exit_content, i)
                else:
                    # Try to extract unquoted identifier
                    destination, i = self._extract_identifier(exit_content, i)
                
                if destination and direction:
                    # Context-aware resolution for KITCHEN-WINDOW 
                    if destination == "KITCHEN-WINDOW":
                        # KITCHEN-WINDOW is a bidirectional door between KITCH and EHOUS
                        # Need to determine context from parent room ID that will be set later
                        # For now, store as special marker to be resolved in room_loader
                        exits[direction.lower()] = "KITCHEN-WINDOW-MARKER"  
                    else:
                        exits[direction.lower()] = destination
                    
            else:
                # Not a quoted direction, skip this token
                i += 1
        
        return exits

    def _extract_quoted_string(self, text: str, start: int) -> Tuple[Optional[str], int]:
        """Extract a quoted string starting at position start."""
        if start >= len(text) or text[start] != '"':
            return None, start
            
        i = start + 1
        result = ""
        
        while i < len(text) and text[i] != '"':
            result += text[i]
            i += 1
            
        if i < len(text) and text[i] == '"':
            i += 1  # Skip closing quote
            
        return result if result else None, i

    def _skip_nexit(self, text: str, start: int) -> int:
        """Skip a #NEXIT structure."""
        # Skip until we find the end of the message
        i = start
        while i < len(text) and text[i:i+6] != '#NEXIT':
            i += 1
            
        if i < len(text):
            i += 6  # Skip '#NEXIT'
            
        # Skip whitespace
        while i < len(text) and text[i].isspace():
            i += 1
            
        # Skip the quoted message if present
        if i < len(text) and text[i] == '"':
            _, i = self._extract_quoted_string(text, i)
            
        return i

    def _parse_door_structure(self, text: str, start: int) -> Tuple[Optional[str], int]:
        """Parse a DOOR structure: <DOOR "object" "room1" "room2" "message">"""
        if not text[start:].startswith('<DOOR'):
            return None, start
            
        # Find the end of the DOOR structure
        bracket_count = 0
        i = start
        
        while i < len(text):
            if text[i] == '<':
                bracket_count += 1
            elif text[i] == '>':
                bracket_count -= 1
                if bracket_count == 0:
                    break
            i += 1
            
        if bracket_count != 0:
            return None, i
            
        door_content = text[start:i+1]
        
        # Extract the rooms from the DOOR structure
        # Format: <DOOR "object" "room1" "room2" "message">
        quoted_strings = re.findall(r'"([^"]*)"', door_content)
        
        if len(quoted_strings) >= 3:
            # Use room1 as the primary destination (could be enhanced to be smarter)
            return quoted_strings[1], i + 1
            
        return None, i + 1

    def _parse_cexit_structure(self, text: str, start: int) -> Tuple[Optional[str], int]:
        """Parse a CEXIT structure: <CEXIT "flag" "room" "message" <> action>"""
        if not text[start:].startswith('<CEXIT'):
            return None, start
            
        # Find the end of the CEXIT structure
        bracket_count = 0
        i = start
        
        while i < len(text):
            if text[i] == '<':
                bracket_count += 1
            elif text[i] == '>':
                bracket_count -= 1
                if bracket_count == 0:
                    break
            i += 1
            
        if bracket_count != 0:
            return None, i
            
        cexit_content = text[start:i+1]
        
        # Extract the room from the CEXIT structure  
        # Format: <CEXIT "flag" "room" "message" <> action>
        quoted_strings = re.findall(r'"([^"]*)"', cexit_content)
        
        if len(quoted_strings) >= 2:
            # Room is usually the second quoted string
            return quoted_strings[1], i + 1
            
        return None, i + 1

    def _skip_structure(self, text: str, start: int) -> int:
        """Skip an unknown < > structure."""
        bracket_count = 0
        i = start
        
        while i < len(text):
            if text[i] == '<':
                bracket_count += 1
            elif text[i] == '>':
                bracket_count -= 1
                if bracket_count == 0:
                    break
            i += 1
            
        return i + 1 if i < len(text) else i

    def _extract_variable_ref(self, text: str, start: int) -> Tuple[Optional[str], int]:
        """Extract a variable reference like ,MR-G"""
        if start >= len(text) or text[start] != ',':
            return None, start
            
        i = start + 1
        result = ""
        
        # Extract identifier characters
        while i < len(text) and (text[i].isalnum() or text[i] in '-_'):
            result += text[i]
            i += 1
            
        # Resolve key variables to their actual room destinations
        # Based on analysis of original .mud files
        variable_mappings = {
            # Kitchen/House connections - DOOR objects need context-aware resolution 
            # KITCHEN-WINDOW connects KITCH<->EHOUS bidirectionally
            "KITCHEN-WINDOW": "KITCHEN-WINDOW",  # Special marker for context resolution
            
            # Tree climbing attempts (blocked exits)
            "NOTREE": None,  # #NEXIT "There is no tree here suitable for climbing."
            
            # Water/dam areas
            "CURRENT": None,  # #NEXIT "The current is too strong."
            "CLIFFS": None,  # #NEXIT related to cliffs
            
            # Mirror room variables
            "MR-G": "MRG",
            "MR-A": "MRA", 
            "MR-B": "MRB",
            "MR-C": "MRC",
            "MR-D": "MRD", 
            "MIREX": "INMIR",  # Mirror entrance
            "MOUT": "MRA",     # Mirror exit
            
            # Endgame variables
            "CD": "FDOOR",     # Closed door
            "OD": "FDOOR",     # Open door  
            "WD": "FDOOR",     # Wooden door
            "FOUT": None,      # Blocked exit
            
            # Bank variables
            "BKALARM": None,   # Bank alarm system
            
            # Other common blocked exits
            "CXGNOME": None,   # Blocked by gnome
            "DOME-FLAG": None, # Conditional exit
            
            # Add the specific ones causing our issues
            "XBIN": None,
            "XCIN": None, 
            "LEDIN": None,
            "SAFIN": None,
        }
        
        resolved = variable_mappings.get(result)
        if resolved is None:
            # This is a blocked exit or unresolved variable - skip it
            return None, i
        else:
            return resolved, i

    def _extract_identifier(self, text: str, start: int) -> Tuple[Optional[str], int]:
        """Extract an unquoted identifier."""
        i = start
        result = ""
        
        # Extract identifier characters until whitespace or special chars
        while i < len(text) and (text[i].isalnum() or text[i] in '-_'):
            result += text[i]
            i += 1
            
        return result if result else None, i
    
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