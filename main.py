from entities import GameObject, Room, Player, Action
from parsers import parse_exits, parse_objects, parse_flags, parse_action
from typing import Optional, List, Dict
import re

def load_rooms():
    import glob
    rooms = {}
    mud_files = glob.glob("zork_mtl_source/*.mud")
    room_id: Optional[str] = None
    desc_long: Optional[str] = None
    desc_short: Optional[str] = None
    exits: Dict[str, str] = {}
    objects: List[GameObject] = []
    flags: List[str] = []
    action: Optional[str] = None
    # ...existing parsing logic...
    if not rooms:
        # Add a fallback room for demo/testing
        rooms["WHOUS"] = Room(
            id="WHOUS",
            desc_long="You are standing west of a white house. There is a door to the east.",
            desc_short="West of House",
            exits={"east": "HOUSE"},
            objects=[GameObject("Welcome Mat", "A simple mat lies here.")],
            flags=[],
            action=None
        )
        rooms["HOUSE"] = Room(
            id="HOUSE",
            desc_long="You are inside the white house. There is a door to the west.",
            desc_short="Inside House",
            exits={"west": "WHOUS"},
            objects=[],
            flags=[],
            action=None
        )
    return rooms

class Game:
    def __init__(self):
        self.rooms: Dict[str, Room] = load_rooms()
        self.current_room: Optional[str] = self._get_start_room()
        self.inventory: List[GameObject] = []

    def _get_start_room(self):
        # Canonical starting room is 'WHOUS' (West of House) per MUD source
        if not self.rooms:
            print("Error: No rooms loaded. Check your room source files or parser.")
            return None
        # Try canonical ID first
        if "WHOUS" in self.rooms:
            return "WHOUS"
        # Try common aliases
        for room_id in self.rooms:
            if room_id.lower() in ["west of house", "whoos", "start"]:
                return room_id
        # Fallback: first available room
        return next(iter(self.rooms))

    def describe_current_room(self):
        if not self.current_room or self.current_room not in self.rooms:
            print("No valid current room.")
            return
        room = self.rooms[self.current_room]
        print(f"\n{room.desc_long}\n")
        if room.exits:
            print("Exits:")
            for direction, dest in room.exits.items():
                print(f"  {direction}: {dest}")
        if room.objects:
            print("Objects:")
            for obj in room.objects:
                print(f"  {obj.name}: {obj.description}")

    def move(self, direction):
        if not self.current_room or self.current_room not in self.rooms:
            print("No valid current room.")
            return
        room = self.rooms[self.current_room]
        if direction in room.exits:
            dest = room.exits[direction]
            if dest in self.rooms:
                self.current_room = dest
                self.describe_current_room()
            else:
                print(f"Can't go {direction}: destination room not found.")
        else:
            print(f"No exit in direction '{direction}'.")

    def look(self):
        self.describe_current_room()

    def show_inventory(self):
        if self.inventory:
            print("Inventory:")
            for obj in self.inventory:
                print(f"  {obj.name}: {obj.description}")
        else:
            print("Your inventory is empty.")

    def parse_command(self, command: str):
        cmd = command.strip().lower()
        # Canonical commands from MUD source
        if cmd in ["quit", "exit"]:
            print("Thanks for playing!")
            return False
        elif cmd in ["look", "l"]:
            self.look()
            return True
        # Cardinal direction short commands
        cardinal_dirs = ["n", "s", "e", "w", "ne", "nw", "se", "sw", "u", "d", "up", "down"]
        if cmd in cardinal_dirs:
            self.move(cmd)
            return True
        elif cmd.startswith("go ") or cmd.startswith("move "):
            direction = cmd.split(" ", 1)[1] if " " in cmd else ""
            self.move(direction)
            return True
        elif self.current_room and self.current_room in self.rooms and cmd in self.rooms[self.current_room].exits:
            self.move(cmd)
            return True
        elif cmd in ["inventory", "i"]:
            self.show_inventory()
            return True
        # Object interaction: get/take
        elif cmd.startswith("get ") or cmd.startswith("take "):
            obj_name = cmd.split(" ", 1)[1]
            room = self.rooms.get(self.current_room) if self.current_room and self.current_room in self.rooms else None
            if room:
                obj = next((o for o in room.objects if o.name.lower() == obj_name), None)
                if obj:
                    self.inventory.append(obj)
                    room.objects.remove(obj)
                    print(f"You take the {obj.name}.")
                else:
                    print(f"There is no {obj_name} here.")
            else:
                print("No room loaded.")
            return True
        # Object interaction: drop/put/throw
        elif any(cmd.startswith(x + " ") for x in ["drop", "put", "throw"]):
            obj_name = cmd.split(" ", 1)[1]
            obj = next((o for o in self.inventory if o.name.lower() == obj_name), None)
            if obj:
                self.inventory.remove(obj)
                room = self.rooms.get(self.current_room) if self.current_room and self.current_room in self.rooms else None
                if room:
                    room.objects.append(obj)
                    print(f"You drop the {obj.name}.")
                else:
                    print("No room loaded.")
            else:
                print(f"You don't have a {obj_name}.")
            return True
        # Object interaction: examine/search
        elif any(cmd.startswith(x + " ") for x in ["examine", "search"]):
            obj_name = cmd.split(" ", 1)[1]
            obj = next((o for o in self.inventory if o.name.lower() == obj_name), None)
            if not obj:
                room = self.rooms.get(self.current_room) if self.current_room and self.current_room in self.rooms else None
                if room:
                    obj = next((o for o in room.objects if o.name.lower() == obj_name), None)
            if obj:
                print(f"{obj.name}: {obj.description}")
            else:
                print(f"You see no {obj_name} to examine.")
            return True
        # Basic stubs for other commands
        elif cmd in ["get", "take"]:
            print("Specify what to take, e.g. 'get mat'.")
            return True
        elif cmd in ["drop", "put", "throw"]:
            print("Specify what to drop, e.g. 'drop mat'.")
            return True
        elif cmd in ["open"] or cmd.startswith("open "):
            print("[Stub] You try to open something.")
            return True
        elif cmd in ["close"] or cmd.startswith("close "):
            print("[Stub] You try to close something.")
            return True
        elif cmd in ["read"] or cmd.startswith("read "):
            print("[Stub] You try to read something.")
            return True
        elif cmd in ["eat", "drink"] or any(cmd.startswith(x + " ") for x in ["eat", "drink"]):
            print("[Stub] You try to eat/drink something.")
            return True
        elif cmd in ["climb", "jump", "swim"] or any(cmd.startswith(x + " ") for x in ["climb", "jump", "swim"]):
            print("[Stub] You try to climb/jump/swim.")
            return True
        elif cmd in ["attack"] or cmd.startswith("attack "):
            print("[Stub] You try to attack.")
            return True
        elif cmd in ["help"]:
            print("[Stub] Help: Available commands are look, go, inventory, get, drop, open, close, read, eat, drink, climb, jump, swim, attack, help, save, restore, restart, score, wait, listen, examine, search, unlock, lock, turn, push, pull, light, extinguish, wear, remove, quit.")
            return True
        elif cmd in ["save"]:
            print("[Stub] Save feature not implemented.")
            return True
        elif cmd in ["restore"]:
            print("[Stub] Restore feature not implemented.")
            return True
        elif cmd in ["restart"]:
            print("[Stub] Restart feature not implemented.")
            return True
        elif cmd in ["score"]:
            print("[Stub] Your score is 0.")
            return True
        elif cmd in ["wait"]:
            print("[Stub] You wait a moment.")
            return True
        elif cmd in ["listen"]:
            print("[Stub] You listen carefully.")
            return True
        elif cmd in ["unlock", "lock"] or any(cmd.startswith(x + " ") for x in ["unlock", "lock"]):
            print("[Stub] You try to unlock/lock something.")
            return True
        elif cmd in ["turn", "push", "pull"] or any(cmd.startswith(x + " ") for x in ["turn", "push", "pull"]):
            print("[Stub] You try to turn/push/pull something.")
            return True
        elif cmd in ["light", "extinguish"] or any(cmd.startswith(x + " ") for x in ["light", "extinguish"]):
            print("[Stub] You try to light/extinguish something.")
            return True
        elif cmd in ["wear", "remove"] or any(cmd.startswith(x + " ") for x in ["wear", "remove"]):
            print("[Stub] You try to wear/remove something.")
            return True
        else:
            print("Unknown command. Try 'look', 'go <direction>', 'inventory', or 'quit'.")
            return True

if __name__ == "__main__":
    print("Welcome to Phork! Type 'look' to see your surroundings, 'go <direction>' to move, 'inventory' to check your items, or 'quit' to exit.")
    game = Game()
    game.describe_current_room()
    while True:
        command = input("\n> ")
        if not game.parse_command(command):
            break


