"""
Phork: A Text-Based Adventure Game
MIT License
Inspired by Zork, written from scratch using only original MDL source as reference.
"""

import sys

class Room:
    def __init__(self, name, description, exits=None, objects=None):
        self.name = name
        self.description = description
        self.exits = exits or {}
        self.objects = objects or []

class Game:
    def __init__(self):
        self.rooms = {}
        self.current_room = None
        self.inventory = []

    def describe(self):
        room = self.rooms[self.current_room]
        print(f"\n{room.name}\n{room.description}")
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
        {"east": "Kitchen"}
    )
    game.rooms["Kitchen"] = Room(
        "Kitchen",
        "You are in the kitchen. There is a table here.",
        {"west": "West of House"}
    )
    game.current_room = "West of House"
    game.run()

if __name__ == "__main__":
    main()
