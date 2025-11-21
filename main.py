# Generic .mud file parser
def parse_mud_file(filepath, tag_patterns):
    """
    Parse a .mud file and extract data based on tag_patterns.
    tag_patterns: dict of {tag: regex_pattern}
    Returns: dict of {tag: [matches]}
    """
    import re
    results = {tag: [] for tag in tag_patterns}
    try:
        with open(filepath, "r") as f:
            content = f.read()
        for tag, pattern in tag_patterns.items():
            matches = re.findall(pattern, content)
            results[tag].extend(matches)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    return results

# Example usage for objects, actions, flags, etc.
# tag_patterns = {
#     "object": r'<OBJ\s+"([^"]+)"\s+"([^"]+)"',
#     "action": r'<DEFINE\s+([A-Z0-9_-]+)',
#     "flag": r'<FLAGWORD\s+([\w\s]+)>'
# }
# objects_data = parse_mud_file("zork_mtl_source/prim.mud", tag_patterns)
"""
Phork: A Text-Based Adventure Game
MIT License
Inspired by Zork, written from scratch using only original MDL source as reference.
"""

from __future__ import annotations
import sys
from typing import List, Dict, Optional, Any

"""
Core gameplay data structures for Zork-like game.
"""

class Room:
    def __init__(self, id: str, desc_long: str, desc_short: str, exits: Dict[str, str], objects: List['GameObject'] = None, flags: list = None, action: str = None):
        self.id = id
        self.desc_long = desc_long
        self.desc_short = desc_short
        self.exits = exits  # direction -> room id
        self.objects = objects if objects else []
        self.visited = False
        self.flags = flags if flags else []
        self.action = action

class GameObject:
    def __init__(self, name: str, description: str, location: Optional[str] = None):
        self.name = name
        self.description = description
        self.location = location  # room id or 'inventory'

class Player:
    def __init__(self, name: str, current_room: str):
        self.name = name
        self.current_room = current_room
        self.inventory: List[GameObject] = []

class Action:
    def __init__(self, name: str, function):
        self.name = name
        self.function = function  # Callable for action logic

# Example usage (to be expanded in later steps)

actions: Dict[str, Action] = {}
player: Optional[Player] = None

class Game:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.current_room: Optional[str] = None
        self.inventory: List[GameObject] = []

    def parse_command(self, command: str):
        command = command.strip().lower()
        directions = ["north", "south", "east", "west"]
        if command in directions:
            self.move(command)
            return
        if command in ["look"]:
            self.describe()
            return
        if command in ["quit", "exit"]:
            print("Thanks for playing Phork!")
            exit(0)
        print("I don't understand that command.")

    def describe(self):
        room = self.rooms[self.current_room]
        print(f"\n{room.id}\n{room.desc_long}")
        print("Exits: " + ", ".join(room.exits.keys()))

    def move(self, direction):
        room = self.rooms[self.current_room]
        if direction in room.exits:
            self.current_room = room.exits[direction]
            self.describe()
        else:
            print("You can't go that way.")

    def run(self):
        self.describe()
        while True:
            try:
                command = input("\n> ")
                self.parse_command(command)
            except (EOFError, KeyboardInterrupt):
                print("\nThanks for playing Phork!")
                break

    def run(self):
        self.describe()
        while True:
            try:
                command = input("\n> ")
                self.parse_command(command)
            except (EOFError, KeyboardInterrupt):
                print("\nThanks for playing Phork!")
                break


import re


# Expandable tag parsers
def parse_exits(line):
    exits = {}
    matches = re.findall(r'<EXIT\s+"(\w+)"\s+"([^"]+)"', line)
    for direction, dest in matches:
        exits[direction] = dest
    return exits

def parse_objects(line):
    objects = []
    matches = re.findall(r'<OBJ\s+"([^"]+)"\s+"([^"]+)"(?:\s+([\w\s]+))?', line)
    for match in matches:
        name, desc, *rest = match
        obj = GameObject(name, desc)
        # Future: parse additional attributes from rest
        objects.append(obj)
    return objects

def parse_flags(line):
    # Example: <FLAGWORD RSEENBIT RLIGHTBIT ...>
    flags = re.findall(r'<FLAGWORD\s+([\w\s]+)>', line)
    return flags[0].split() if flags else []

def parse_action(line):
    # Example: <RACTION "some_action">
    match = re.search(r'<RACTION\s+"([^"]+)"', line)
    return match.group(1) if match else None

def load_rooms():
    rooms = {}
    try:
        with open("zork_mtl_source/rooms.mud", "r") as f:
            lines = f.readlines()
        room_id = None
        desc_long = None
        desc_short = None
        exits = {}
        objects = []
        flags = []
        action = None
        for line in lines:
            line = line.strip()
            if line.startswith('<ROOM'):
                if room_id:
                    # Room can be extended with flags and action
                    room = Room(room_id, desc_long or "", desc_short or "", exits, objects)
                    room.flags = flags
                    room.action = action
                    rooms[room_id] = room
                parts = line.split('"')
                room_id = parts[1] if len(parts) > 1 else None
                desc_long = None
                desc_short = None
                exits = {}
                objects = []
                flags = []
                action = None
            elif room_id and line.startswith('"'):
                if not desc_long:
                    desc_long = line.strip('"')
                elif not desc_short:
                    desc_short = line.strip('"')
            elif room_id and '<EXIT' in line:
                exits.update(parse_exits(line))
            elif room_id and '<OBJ' in line:
                objects.extend(parse_objects(line))
            elif room_id and '<FLAGWORD' in line:
                flags.extend(parse_flags(line))
            elif room_id and '<RACTION' in line:
                action = parse_action(line)
        if room_id:
            room = Room(room_id, desc_long or "", desc_short or "", exits, objects)
            room.flags = flags
            room.action = action
            rooms[room_id] = room
    except Exception as e:
        print(f"Error loading rooms: {e}. Using fallback rooms.")
        rooms["West of House"] = Room(
            "West of House",
            "You are standing in an open field west of a white house, with a boarded front door.",
            "Field west of house.",
            {"east": "Kitchen"}
        )
        rooms["Kitchen"] = Room(
            "Kitchen",
            "You are in the kitchen. There is a table here.",
            "Kitchen.",
            {"west": "West of House"}
        )
    return rooms

def main():
    game = Game()
    game.rooms = load_rooms()
    game.current_room = "West of House"
    game.run()
