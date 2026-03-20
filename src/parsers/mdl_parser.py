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
        self.variables: Dict[str, str] = {}  # Variable name -> value lookup
        
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
        
        # Find the end of this room definition
        remaining_text = text[room_start:]
        
        # Look for the complete room structure by counting < and > brackets
        bracket_count = 0
        pos = 0
        found_first_bracket = False
        
        while pos < len(remaining_text):
            char = remaining_text[pos]
            if char == '<':
                bracket_count += 1
                found_first_bracket = True
            elif char == '>' and found_first_bracket:
                bracket_count -= 1
                # When bracket count reaches 0, we've found the end of our room
                if bracket_count == 0:
                    break
            pos += 1
        
        if bracket_count != 0:
            # Fallback: find the next room or end of text
            next_room_pos = remaining_text.find('<ROOM', 1)
            if next_room_pos == -1:
                room_text = remaining_text  # Take rest of file
            else:
                room_text = remaining_text[:next_room_pos]
        else:
            room_text = remaining_text[:pos + 1]
        
        # Debug for LROOM
        if room_id == "LROOM":
            pass  # Debug removed
        
        try:
            room_data = self._parse_room_content(room_id, room_text)
            return room_data, room_start + pos + 1
        except Exception as e:
            print(f"Warning: Failed to parse room {room_id}: {e}")
            return None, room_start + pos + 1
    
    def _parse_room_content(self, room_id: str, room_text: str) -> RoomData:
        """Parse the content within a room definition."""
        
        # Set room context for variable resolution
        self._current_room_id = room_id
        
        # Extract quoted strings and variable references in order
        tokens = []
        
        # Find all quoted strings and variable references
        quotes = list(re.finditer(r'"((?:[^"\\]|\\.)*)"', room_text))
        variables = list(re.finditer(r',([A-Z][A-Z0-9-]*)', room_text))
        
        # Combine and sort by position
        all_tokens = []
        for match in quotes:
            all_tokens.append((match.start(), 'quote', match.group(1)))
        for match in variables:
            all_tokens.append((match.start(), 'variable', match.group(0)))
        
        all_tokens.sort(key=lambda x: x[0])
        
        # Extract values in order, resolving variables
        values = []
        for pos, token_type, value in all_tokens:
            if token_type == 'quote':
                values.append(value)
            elif token_type == 'variable':
                resolved = self._resolve_variable(value)
                values.append(resolved)
        
        # MDL Room format analysis - smart detection of description vs name  
        long_description = ""
        short_name = room_id  # Default fallback
        
        # Skip the room ID (first value) and process remaining values
        if len(values) >= 3:
            # Three or more values: ID, desc, name, ...
            desc_value = values[1].strip()
            name_value = values[2].strip()
            
            # Handle empty description field (like KITCH with "")
            if not desc_value:
                long_description = self._get_canonical_description(room_id)
                short_name = name_value if name_value else self._generate_room_name("", room_id)
            else:
                # Both desc and name provided - use smart detection
                if len(desc_value) > 30 or any(phrase in desc_value.lower() for phrase in ["you are", "this is", "you have come"]):
                    long_description = desc_value
                    short_name = name_value if name_value else self._generate_room_name(desc_value, room_id)
                elif len(name_value) > 30 or any(phrase in name_value.lower() for phrase in ["you are", "this is", "you have come"]):
                    long_description = name_value
                    short_name = desc_value
                else:
                    # Smart assignment based on context
                    long_description = desc_value
                    short_name = name_value
        
        elif len(values) >= 2:
            val1, val2 = values[1].strip(), ""
            
            # Only two values total - handle like before
            if not val1:
                # Empty description field
                long_description = self._get_canonical_description(room_id)
                short_name = self._generate_room_name("", room_id)
            elif len(val1) > 20:
                # Looks like description
                long_description = val1
                short_name = self._generate_room_name(val1, room_id)
            else:
                # Looks like name
                short_name = val1
                long_description = self._get_canonical_description(room_id)
            
        elif len(values) >= 1:
            # Only one value after room ID
            single_value = values[0].strip()
            if len(single_value) > 20:  # Looks like a description
                long_description = single_value
                short_name = self._generate_room_name(single_value, room_id)
            else:  # Looks like a name
                short_name = single_value
                long_description = self._get_canonical_description(room_id)
        
        # Handle empty descriptions by using canonical fallbacks
        if not long_description:
            long_description = self._get_canonical_description(room_id)
        
        # Parse exits
        exits = self._parse_exits(room_text, room_id)
        
        # Parse objects
        objects = self._parse_objects(room_text)
        
        # Parse objects
        objects = self._parse_objects(room_text)
        
        # Parse room flags
        flags = self._parse_flags(room_text)
        
        return RoomData(
            id=room_id,
            long_description=long_description,
            short_name=short_name,
            exits=exits,
            objects=objects,
            flags=flags
        )
    
    def _get_canonical_description(self, room_id: str) -> str:
        """Get canonical descriptions for rooms with empty descriptions in the .mud files."""
        
        # These descriptions come from the original PSETG definitions in dung.mud
        canonical_descriptions = {
            "LROOM": "You are in the living room.  There is a door to the east.  To the west is a cyclops-shaped hole in an old wooden door, above which is some strange gothic lettering in an ancient tongue, roughly translating to \"This space intentionally left blank.\"",
            
            "KITCH": "You are in the kitchen of the white house.  A table seems to have been used recently for the preparation of food.  A passage leads to the west and a dark staircase can be seen leading upward.  To the east is a small window which is open.",
            
            "CELLA": "You are in a dark and damp cellar with a narrow passageway leading east, and a crawlway to the south.  On the west is the bottom of a steep metal ramp which is unclimbable.",
            
            "MIRR1": "You are in a large square room with tall ceilings.  On the south wall is an enormous mirror which fills the entire wall.  There are exits on the other three sides of the room.",
            
            "MIRR2": "You are in a large square room with tall ceilings.  On the south wall is an enormous mirror which fills the entire wall.  There are exits on the other three sides of the room.",
            
            "TREE": "You are about 10 feet above the ground nestled among some large branches. The nearest branch above you is above your reach.",
            
            "CLEAR": "You are in a clearing in a forest of white trees. Paths lead off in all directions.",
            
            "MGRAT": "You are in a clearing, with a grating visible on the ground. Leaves are piled by the grating; it looks like it has been recently opened.",
            
            # Add more canonical descriptions as needed...
            "DOME": "This is a large room with a prominent doorway leading to a down staircase. To the west is a narrow twisting tunnel, covered with a thin layer of dust. Above you is a large dome painted with scenes depicting elfin hacking rites. Up around the edge of the dome (20 feet up) is a wooden railing. In the center of the room there is a white marble pedestal.",
            
            "LLD2": "You have entered the Land of the Living Dead, a large desolate room. Although it is apparently uninhabited, you can hear the sounds of thousands of lost souls weeping and moaning. In the east corner are stacked the remains of dozens of previous adventurers who were less fortunate than yourself. To the east is an ornate passage, apparently recently constructed. A passage exits to the west.",
            
            "EHOUS": "You are behind the white house.  A path runs around the house to the north and south.  A slight noise can be heard coming from inside.  On the east is a window which is slightly ajar.",
        }
        
        # Handle room type patterns
        if room_id.startswith("DEAD"):
            return "You have come to a dead end in the maze."
        elif room_id.startswith("MAZE") or room_id.startswith("MAZ"):
            return "This is part of a maze of twisty little passages, all alike."
        elif room_id.startswith("FORE"): 
            return "This is a forest, with trees in all directions around you."
        elif room_id.startswith("MINE"):
            return "You are in a mine shaft."
        elif room_id.startswith("RIVR"):
            return "You are on the River Frigid."
            
        return canonical_descriptions.get(room_id, f"You are in {room_id}.")
    
    def _generate_room_name(self, description: str, room_id: str) -> str:
        """Generate a reasonable room name from description if not provided."""
        if not description:
            return room_id
            
        desc_lower = description.lower()
        
        # Special cases for common Zork rooms
        if "west of" in desc_lower and "house" in desc_lower:
            return "West of House"
        elif "north of" in desc_lower and "house" in desc_lower:
            return "North of House"
        elif "south of" in desc_lower and "house" in desc_lower:
            return "South of House"
        elif "behind" in desc_lower and "house" in desc_lower:
            return "Behind House"
        elif "east of" in desc_lower and "house" in desc_lower:
            return "East of House"
        elif "kitchen" in desc_lower and "white house" in desc_lower:
            return "Kitchen"
        elif "living room" in desc_lower:
            return "Living Room"
        elif "attic" in desc_lower:
            return "Attic"
        elif "treasure" in desc_lower and "room" in desc_lower:
            return "Treasure Room"
        elif "cyclops" in desc_lower and "room" in desc_lower:
            return "Cyclops Room"
        else:
            # Use first few words of description as name
            words = description.split()[:3]
            name = " ".join(words).replace(",", "").replace(".", "")
            return name if name else room_id
    
    def _parse_exits(self, room_text: str, room_id: str) -> Dict[str, str]:
        """Parse exits from <EXIT ...> pattern."""
        exits = {}
        
        # Find the start of EXIT block
        exit_start = room_text.find('<EXIT')
        if exit_start == -1:
            return exits
        
        # Find the matching closing bracket by counting nesting
        bracket_count = 0
        i = exit_start
        exit_end = -1
        
        while i < len(room_text):
            if room_text[i] == '<':
                bracket_count += 1
            elif room_text[i] == '>':
                bracket_count -= 1
                if bracket_count == 0:
                    exit_end = i
                    break
            i += 1
        
        if exit_end != -1:
            # Extract content between <EXIT and closing >
            exit_content = room_text[exit_start + 5:exit_end].strip()
            exits = self._parse_exit_content(exit_content, room_id)
        
        return exits
    
    def _parse_objects(self, room_text: str) -> List[str]:
        """Parse objects from object list pattern."""
        objects = []
        
        # Look for parentheses blocks that contain GET-OBJ patterns
        # Use DOTALL to handle multi-line object lists
        paren_matches = re.findall(r'\(([^)]*)\)', room_text, re.DOTALL)
        
        for paren_content in paren_matches:
            # Check if this parentheses block contains GET-OBJ patterns
            if 'GET-OBJ' in paren_content:
                # Extract all GET-OBJ references from this block
                obj_refs = re.findall(r'<GET-OBJ\s+"([^"]+)">', paren_content, re.DOTALL)
                objects.extend(obj_refs)
                # Only process the first GET-OBJ block we find
                break
        
        return objects
    
    def _parse_flags(self, room_text: str) -> List[str]:
        """Parse room flags from flag patterns.""" 
        flags = []
        flag_patterns = re.findall(r'R[A-Z]+BIT', room_text)
        flags.extend(flag_patterns)
        return flags

    def _parse_exit_content(self, exit_content: str, room_id: str) -> Dict[str, str]:
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
                        destination, i = self._parse_door_structure(exit_content, i, room_id)
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
        i = start
        
        # Skip all #NEXIT tokens (there can be multiple)
        while i < len(text) and text[i:i+6] == '#NEXIT':
            i += 6  # Skip '#NEXIT'
            
            # Skip whitespace after #NEXIT
            while i < len(text) and text[i].isspace():
                i += 1
        
        # Skip the optional quoted message if present
        if i < len(text) and text[i] == '"':
            _, i = self._extract_quoted_string(text, i)
            
        return i

    def _parse_door_structure(self, text: str, start: int, current_room_id: str) -> Tuple[Optional[str], int]:
        """Parse a DOOR structure: <DOOR "object" "room1" "room2" "message">
        Returns the OTHER room in the door connection (not current_room_id)."""
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
            # Use room2 as the destination (the third quoted string)
            return quoted_strings[2], i + 1
            
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
    
    def _parse_variables(self, content: str):
        """Parse PSETG and SETG variable definitions from the content."""
        # Find all PSETG and SETG variable assignments
        # Format: <PSETG VARNAME "value"> or <SETG VARNAME "value">
        pattern = r'<(?:P?SETG)\s+([A-Z][A-Z0-9-]*)\s+"([^"]*)">'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        for var_name, var_value in matches:
            self.variables[var_name] = var_value
    
    def _resolve_variable(self, var_ref: str) -> str:
        """Resolve a variable reference like ',STFORE' to its value."""
        if var_ref.startswith(','):
            var_name = var_ref[1:]  # Remove the comma
            value = self.variables.get(var_name, var_ref)
            
            # Special handling for DEAD end rooms - some use DEADEND when they should use SDEADEND  
            if var_name == "DEADEND":
                room_context = getattr(self, '_current_room_id', None)
                if room_context and room_context in ['DEAD3', 'DEAD4', 'DEAD5', 'DEAD6', 'DEAD7']:
                    # These rooms should use the full dead end description
                    return self.variables.get("SDEADEND", "You have come to a dead end in the maze.")
            
            return value  # Return original ref if not found
        return var_ref
    
    def parse_file(self, file_path: Path) -> Dict[str, RoomData]:
        """Parse an entire .mud file and extract all room definitions."""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {}
        
        # First pass: parse all variable definitions
        self._parse_variables(content)
        
        # Second pass: parse rooms
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


    def _extract_balanced_brackets(self, text: str, start_pattern: str) -> Optional[str]:
        """Extract content between balanced angle brackets starting with start_pattern."""
        start_index = text.find(start_pattern)
        if start_index == -1:
            return None
            
        # Find the opening bracket
        bracket_start = text.find('<', start_index)
        if bracket_start == -1:
            return None
            
        # Count brackets to find the matching closing bracket
        bracket_count = 0
        i = bracket_start
        
        while i < len(text):
            if text[i] == '<':
                bracket_count += 1
            elif text[i] == '>':
                bracket_count -= 1
                if bracket_count == 0:
                    # Found the matching closing bracket
                    # Return content between the brackets (excluding the < >)
                    content_start = bracket_start + len(start_pattern)
                    while content_start < i and text[content_start].isspace():
                        content_start += 1
                    
                    return text[content_start:i].strip()
            i += 1
            
        return None


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