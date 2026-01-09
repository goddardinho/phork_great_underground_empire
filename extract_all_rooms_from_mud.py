import re

# Extracts all likely room names from rooms.mud by searching for patterns like <ROOM, <ROOM-INFO, <SFIND-ROOM, and quoted uppercase names

def extract_room_names(mud_path):
    room_names = set()
    # Patterns for various room definitions
    patterns = [
        re.compile(r'<SFIND-ROOM\s+"([A-Z0-9\-]+)"'),
        re.compile(r'<ROOM-INFO(?:\s+\d+)?\s*"?([A-Z0-9\-]+)"?'),
        re.compile(r'<ROOM\s+"([A-Z0-9\-]+)"'),
        re.compile(r'\(ROOM\s+([A-Z0-9\-]+)\)'),
        re.compile(r'"([A-Z0-9\-]+)"'),  # fallback: quoted uppercase names
    ]
    with open(mud_path, 'r') as f:
        for line in f:
            for pat in patterns:
                for match in pat.findall(line):
                    # Some patterns return tuples, some strings
                    if isinstance(match, tuple):
                        for m in match:
                            if m.isupper() and len(m) > 2:
                                room_names.add(m)
                    elif isinstance(match, str):
                        if match.isupper() and len(match) > 2:
                            room_names.add(match)
    return sorted(room_names)

def main():
    mud_path = "zork_mtl_source/rooms.mud"
    rooms = extract_room_names(mud_path)
    print("Extracted room names from rooms.mud:")
    for name in rooms:
        print(name)
    print(f"\nTotal unique rooms found: {len(rooms)}")

if __name__ == "__main__":
    main()
