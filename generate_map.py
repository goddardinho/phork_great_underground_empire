
import re
import json
import os

def get_mud_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.mud')]

def extract_define_blocks(text):
    # Find all <DEFINE ROOMNAME ...> blocks
    pattern = re.compile(r'<DEFINE\s+([A-Z0-9_-]+)[^<]*\(([^)]*)\)[^<]*<COND([\s\S]*?)(?=<DEFINE|$)', re.MULTILINE)
    return pattern.findall(text)

def extract_exits_from_block(block_text):
    exits = {}
    # Find <GOTO <SFIND-ROOM "ROOMNAME">>
    for match in re.findall(r'<GOTO\s+<SFIND-ROOM\s+"([A-Z0-9_-]+)">>', block_text):
        exits["GOTO"] = match
    # Find <SFIND-ROOM "ROOMNAME"> in other contexts
    for match in re.findall(r'<SFIND-ROOM\s+"([A-Z0-9_-]+)">', block_text):
        exits["SFIND-ROOM"] = match
    # Find <REXITS ...> vectors
    rexits = re.findall(r'<REXITS\s+<VECTOR([\s\S]*?)>', block_text)
    for vector in rexits:
        # Example: "NORTH" <FIND-ROOM "KITCH"> ...
        exit_pairs = re.findall(r'"([A-Z]+)"\s+<FIND-ROOM\s+"([A-Z0-9_-]+)">', vector)
        for direction, dest in exit_pairs:
            exits[direction] = dest
    # Also look for <EXIT ...>, <CEXIT ...>, <NEXIT ...>
    for tag in ["EXIT", "CEXIT", "NEXIT", "DOOR"]:
        exit_matches = re.findall(rf'<{tag}\\s+"([A-Z]+)"\\s+<FIND-ROOM\\s+"([A-Z0-9_-]+)">', block_text)
        for direction, dest in exit_matches:
            exits[direction] = dest
    return exits

def extract_rooms_and_exits_from_files(filepaths):
    rooms = {}
    for filepath in filepaths:
        with open(filepath, 'r') as f:
            text = f.read()
            define_blocks = extract_define_blocks(text)
            for roomname, args, cond_block in define_blocks:
                exits = extract_exits_from_block(cond_block)
                rooms[roomname] = {"exits": exits}
    return rooms

def build_graph(rooms):
    nodes = list(rooms.keys())
    edges = []
    for room, data in rooms.items():
        exits = data.get("exits", {})
        for direction, dest in exits.items():
            edges.append({"from": room, "to": dest, "direction": direction})
    return {"nodes": nodes, "edges": edges}

def main():
    mud_files = get_mud_files('zork_mtl_source')
    rooms = extract_rooms_and_exits_from_files(mud_files)
    graph = build_graph(rooms)
    with open('map.json', 'w') as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
    main()
