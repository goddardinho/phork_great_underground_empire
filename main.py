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
    def __init__(self, id: str, desc_long: str, desc_short: str, exits: Dict[str, str], objects: List['GameObject'] = None):
        self.id = id
        self.desc_long = desc_long
        self.desc_short = desc_short
        self.exits = exits  # direction -> room id
        self.objects = objects if objects else []
        self.visited = False

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
                command = input("\n> ").strip().lower()
                if command in ["quit", "exit"]:
                    print("Thanks for playing Phork!")
                    break
                elif command in ["look"]:
                    self.describe()
                elif command in ["north", "south", "east", "west"]:
                    self.move(command)
                else:
                    print("I don't understand that command.")
            except (EOFError, KeyboardInterrupt):
                print("\nThanks for playing Phork!")
                break

def main():
    game = Game()
    # TODO: Extract rooms from zork_mtl_source/rooms.mud and initialize game.rooms
    # For now, add a placeholder room
    game.rooms["West of House"] = Room(
        "West of House",
        "You are standing in an open field west of a white house, with a boarded front door.",
        "Field west of house.",
        {"east": "Kitchen"}
    )
    game.rooms["Kitchen"] = Room(
        "Kitchen",
        "You are in the kitchen. There is a table here.",
        "Kitchen.",
        {"west": "West of House"}
    )
    game.current_room = "West of House"
    game.run()

if __name__ == "__main__":
    main()
