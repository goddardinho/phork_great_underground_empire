import re

# Path to the original Zork MUD source file
def extract_room_names(mud_path):
    room_names = set()
    pattern = re.compile(r'<SFIND-ROOM\s+"([A-Z0-9\-]+)"')
    with open(mud_path, 'r') as f:
        for line in f:
            for match in pattern.findall(line):
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
