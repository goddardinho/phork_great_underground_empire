from entities import GameObject, Room, Player, Action
from parsers import parse_exits, parse_objects, parse_flags, parse_action
from typing import Optional, List, Dict
import re
import pickle


def load_rooms():
    import glob

    rooms = {}
    mud_files = glob.glob("zork_mtl_source/*.mud")
    room_id: Optional[str] = None
    desc_long: Optional[str] = None
    desc_short: Optional[str] = None
    exits: Dict[str, str] = {}
    objects: List[GameObject] = []
    # flags are handled per-room, not as a local variable here
    action: Optional[str] = None
    # ...existing parsing logic...
    if not rooms:
        # Add a fallback room for demo/testing
        rooms["WHOUS"] = Room(
            id="WHOUS",
            desc_long="You are standing west of a white house. There is a door to the east.",
            desc_short="West of House",
            exits={"east": "HOUSE"},
            objects=[
                GameObject(
                    "Welcome Mat", "A simple mat lies here.", attributes={"osize": 1}
                ),
                GameObject(
                    "Lantern", "A brass lantern, unlit.", attributes={"osize": 2}
                ),
                GameObject(
                    "Sword", "A sharp sword gleams here.", attributes={"osize": 3}
                ),
                GameObject(
                    "Leaflet", "A small leaflet with writing.", attributes={"osize": 1}
                ),
                GameObject(
                    "Mailbox", "A small mailbox, closed.", attributes={"osize": 4}
                ),
                GameObject("Key", "A small key.", attributes={"osize": 1}),
                GameObject(
                    "Robot", "A silent robot stands here.", attributes={"osize": 10}
                ),
                GameObject(
                    "Treasure Chest", "A heavy chest, locked.", attributes={"osize": 10}
                ),
            ],
            flags=["dark"],
            action=None,
        )
        rooms["HOUSE"] = Room(
            id="HOUSE",
            desc_long="You are inside the white house. There is a door to the west.",
            desc_short="Inside House",
            exits={"west": "WHOUS"},
            objects=[],
            flags=[],
            action=None,
        )
    return rooms


class Game:
    BIGFIX = 9999  # Canonical value for uncarryable objects
    LOAD_MAX = 10  # Canonical Zork I carry limit (adjust as needed)

    # No stray flags assignment here
    def is_room_dark(self, room_id=None):
        room = self.rooms.get(room_id or self.current_room)
        if not room:
            return False
        # Room is dark if it has the 'dark' flag and no light source is present
        if "dark" in getattr(room, "flags", []):
            # Check for lit lantern in inventory
            for obj in self.inventory:
                if obj.name.lower() == "lantern" and getattr(obj, "attributes", {}).get(
                    "lit", False
                ):
                    return False
            return True
        return False

    def check_grue_danger(self):
        # Only trigger grue danger if room is dark and no lit lantern is present
        if self.is_room_dark():
            self.dark_moves += 1
            if self.dark_moves == 1:
                print("It is pitch black. You are likely to be eaten by a grue!")
            elif self.dark_moves >= 2:
                print("Oh no! You have been eaten by a grue.")
                exit()
        else:
            self.dark_moves = 0  # Reset counter if not in darkness

    def __init__(self, demo_mode=False):
        self.dark_moves = 0  # Track moves/actions in darkness
        self.mailbox_open = False
        self.leaflet_taken = False
        self.lantern_lit = False
        self.rooms = load_rooms()
        self.current_room = self._get_start_room()
        self.inventory = []
        self.score = 0
        self.flags = {}  # e.g., dark, dangerous, locked, etc.
        self.puzzles = {}  # Track puzzle states by room or puzzle name
        self.demo_mode = demo_mode
        if self.demo_mode:
            # Give player all objects from starting room, ignore carry limit
            room = self.rooms.get(self.current_room)
            if room and room.objects:
                self.inventory.extend(room.objects)
                room.objects.clear()
            print(
                "[Demo Mode] All objects have been added to your inventory. Carry limits are disabled."
            )

    def get_inventory_weight(self):
        if self.demo_mode:
            return 0

        def obj_weight(obj):
            weight = (
                obj.attributes.get("osize")
                if hasattr(obj, "attributes") and "osize" in obj.attributes
                else getattr(obj, "osize", 1)
            )
            if weight == self.BIGFIX:
                return 0
            return weight

        return sum(obj_weight(o) for o in self.inventory)

    def save_game(self, filename="savegame.pkl"):
        state = {
            "rooms": self.rooms,
            "current_room": self.current_room,
            "inventory": self.inventory,
            "score": self.score,
            "flags": self.flags,
            "puzzles": self.puzzles,
        }
        try:
            with open(filename, "wb") as f:
                pickle.dump(state, f)
            print(f"Game saved to {filename}.")
        except Exception as e:
            print(f"Error saving game: {e}")

    def load_game(self, filename="savegame.pkl"):
        try:
            with open(filename, "rb") as f:
                state = pickle.load(f)
            self.rooms = state.get("rooms", self.rooms)
            self.current_room = state.get("current_room", self.current_room)
            self.inventory = state.get("inventory", self.inventory)
            self.score = state.get("score", self.score)
            self.flags = state.get("flags", self.flags)
            self.puzzles = state.get("puzzles", self.puzzles)
            print(f"Game loaded from {filename}.")
            self.describe_current_room()
        except Exception as e:
            print(f"Error loading game: {e}")

    def check_room_flags(self):
        room = (
            self.rooms.get(self.current_room)
            if self.current_room and self.current_room in self.rooms
            else None
        )
        if not room:
            return
            if self.check_grue_danger():
                exit()
        # Example: handle dark rooms
        if "dark" in room.flags:
            print("It is pitch dark. You are likely to be eaten by a grue.")
        # Example: handle locked rooms
        if "locked" in room.flags:
            print("The room is locked.")
        # Add more flag logic as needed
        if self.check_grue_danger():
            exit()

    def check_puzzles(self):
        # Placeholder for puzzle logic
        # Example: check if a puzzle in the current room is solved
        puzzle_key = f"{self.current_room}_puzzle"
        if self.puzzles.get(puzzle_key):
            print("You have solved the puzzle in this room!")
        # Add more puzzle logic as needed

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
        self.check_room_flags()
        self.check_puzzles()
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
                self.check_grue_danger()
            else:
                print(f"Can't go {direction}: destination room not found.")
        else:
            print(f"No exit in direction '{direction}'.")

    def look(self):
        self.describe_current_room()
        self.check_grue_danger()

    def light_lantern(self):
        lantern = next((o for o in self.inventory if o.name.lower() == "lantern"), None)
        if lantern:
            lantern.attributes["lit"] = True
            print("You light the lantern. The room is now illuminated.")
        else:
            print("You don't have a lantern.")

    def extinguish_lantern(self):
        lantern = next((o for o in self.inventory if o.name.lower() == "lantern"), None)
        if lantern:
            lantern.attributes["lit"] = False
            print("You extinguish the lantern. Darkness returns.")
        else:
            print("You don't have a lantern.")

    # ...existing code...
    # Place this inside parse_command:
    # if cmd in ["light lantern", "turn on lantern"]:
    #     self.light_lantern()
    #     return True
    # elif cmd in ["extinguish lantern", "turn off lantern"]:
    #     self.extinguish_lantern()
    #     return True

    def show_inventory(self):
        if self.inventory:
            print("Inventory:")
            for obj in self.inventory:
                # Try to get weight from attributes first, fallback to osize property, then 1
                weight = (
                    obj.attributes.get("osize")
                    if hasattr(obj, "attributes") and "osize" in obj.attributes
                    else getattr(obj, "osize", 1)
                )
                print(f"  {obj.name}: {obj.description} (weight: {weight})")
            print(
                f"Total carried weight: {self.get_inventory_weight()} / {self.LOAD_MAX}"
            )
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
        cardinal_dirs = [
            "n",
            "s",
            "e",
            "w",
            "ne",
            "nw",
            "se",
            "sw",
            "u",
            "d",
            "up",
            "down",
        ]
        if cmd in cardinal_dirs:
            self.move(cmd)
            return True
        elif cmd.startswith("go ") or cmd.startswith("move "):
            direction = cmd.split(" ", 1)[1] if " " in cmd else ""
            self.move(direction)
            return True
        elif (
            self.current_room
            and self.current_room in self.rooms
            and cmd in self.rooms[self.current_room].exits
        ):
            self.move(cmd)
            return True
        elif cmd in ["inventory", "i"]:
            self.show_inventory()
            return True
        # Object interaction: get/take
        elif cmd.startswith("get ") or cmd.startswith("take "):
            obj_name = cmd.split(" ", 1)[1]
            room = (
                self.rooms.get(self.current_room)
                if self.current_room and self.current_room in self.rooms
                else None
            )
            if obj_name == "all":
                if not room or not room.objects:
                    print("There is nothing here to take.")
                    return True
                taken_any = False
                for obj in list(room.objects):
                    obj_weight = (
                        obj.attributes.get("osize")
                        if hasattr(obj, "attributes") and "osize" in obj.attributes
                        else getattr(obj, "osize", 1)
                    )
                    if obj_weight == self.BIGFIX:
                        obj_weight = 0
                    if (
                        not self.demo_mode
                        and self.get_inventory_weight() + obj_weight > self.LOAD_MAX
                    ):
                        print(
                            f"You can't carry the {obj.name}; it's too heavy or you're overloaded."
                        )
                        continue
                    self.inventory.append(obj)
                    room.objects.remove(obj)
                    print(f"You take the {obj.name}.")
                    taken_any = True
                if not taken_any:
                    print("You couldn't take anything.")
                return True
            if room:
                obj = next(
                    (o for o in room.objects if o.name.lower() == obj_name), None
                )
                if obj:
                    obj_weight = (
                        obj.attributes.get("osize")
                        if hasattr(obj, "attributes") and "osize" in obj.attributes
                        else getattr(obj, "osize", 1)
                    )
                    if obj_weight == self.BIGFIX:
                        obj_weight = 0
                    if (
                        not self.demo_mode
                        and self.get_inventory_weight() + obj_weight > self.LOAD_MAX
                    ):
                        print(
                            f"You cannot carry the {obj.name}. Your load is too heavy."
                        )
                        return True
                    self.inventory.append(obj)
                    room.objects.remove(obj)
                    print(f"You take the {obj.name}.")
                    self.score += 1  # Example: increase score for taking
                else:
                    print(f"There is no {obj_name} here.")
            else:
                print("No room loaded.")
            return True
        # Object interaction: drop/put/throw
        elif any(cmd.startswith(x + " ") for x in ["drop", "put", "throw"]):
            obj_name = cmd.split(" ", 1)[1]
            if obj_name == "all":
                if not self.inventory:
                    print("You have nothing to drop.")
                    return True
                room = (
                    self.rooms.get(self.current_room)
                    if self.current_room and self.current_room in self.rooms
                    else None
                )
                if not room:
                    print("No room loaded.")
                    return True
                for obj in list(self.inventory):
                    self.inventory.remove(obj)
                    room.objects.append(obj)
                    print(f"You drop the {obj.name}.")
                return True
            obj = next((o for o in self.inventory if o.name.lower() == obj_name), None)
            if obj:
                self.inventory.remove(obj)
                room = (
                    self.rooms.get(self.current_room)
                    if self.current_room and self.current_room in self.rooms
                    else None
                )
                if room:
                    room.objects.append(obj)
                    print(f"You drop the {obj.name}.")
                else:
                    print("No room loaded.")
            else:
                print(f"You don't have a {obj_name}.")
            return True
        # Object-specific actions
        elif cmd.startswith("open "):
            obj_name = cmd.split(" ", 1)[1]
            from object_actions import object_action

            if object_action(self, "open", obj_name):
                return True
            print(f"[Stub] You try to open the {obj_name}.")
            return True
        elif cmd.startswith("close "):
            obj_name = cmd.split(" ", 1)[1]
            from object_actions import object_action

            if object_action(self, "close", obj_name):
                return True
            print(f"[Stub] You try to close the {obj_name}.")
            return True
        elif cmd.startswith("look "):
            obj_name = cmd.split(" ", 1)[1]
            from object_actions import object_action

            if object_action(self, "look", obj_name):
                return True
            print(f"[Stub] You try to look at the {obj_name}.")
            return True
        elif cmd.startswith("take "):
            obj_name = cmd.split(" ", 1)[1]
            from object_actions import object_action

            if object_action(self, "take", obj_name):
                return True
            print(f"[Stub] You try to take the {obj_name}.")
            return True
        elif cmd.startswith("read "):
            obj_name = cmd.split(" ", 1)[1]
            from object_actions import object_action

            if object_action(self, "read", obj_name):
                return True
            print(f"[Stub] You try to read the {obj_name}.")
            return True
        elif cmd.startswith("light "):
            obj_name = cmd.split(" ", 1)[1]
            from object_actions import object_action

            if object_action(self, "light", obj_name):
                return True
            print(f"[Stub] You try to light the {obj_name}.")
            return True
        elif cmd.startswith("extinguish "):
            obj_name = cmd.split(" ", 1)[1]
            from object_actions import object_action

            if object_action(self, "extinguish", obj_name):
                return True
            print(f"[Stub] You try to extinguish the {obj_name}.")
            return True
        # Object interaction: eat/drink
        elif any(cmd.startswith(x + " ") for x in ["eat", "drink"]):
            obj_name = cmd.split(" ", 1)[1]
            print(f"[Stub] You try to {cmd.split(' ')[0]} the {obj_name}.")
            return True
        # Object interaction: wear/remove
        elif cmd.startswith("wear "):
            obj_name = cmd.split(" ", 1)[1]
            print(f"[Stub] You try to wear the {obj_name}.")
            return True
        elif cmd.startswith("remove "):
            obj_name = cmd.split(" ", 1)[1]
            print(f"[Stub] You try to remove the {obj_name}.")
            return True
        # Object interaction: light/extinguish
        elif cmd.startswith("light "):
            obj_name = cmd.split(" ", 1)[1]
            print(f"[Stub] You try to light the {obj_name}.")
            return True
        elif cmd.startswith("extinguish "):
            obj_name = cmd.split(" ", 1)[1]
            print(f"[Stub] You try to extinguish the {obj_name}.")
            return True
        # Object interaction: unlock/lock
        elif cmd.startswith("unlock "):
            obj_name = cmd.split(" ", 1)[1]
            print(f"[Stub] You try to unlock the {obj_name}.")
            return True
        elif cmd.startswith("lock "):
            obj_name = cmd.split(" ", 1)[1]
            print(f"[Stub] You try to lock the {obj_name}.")
            return True
        # Object interaction: examine/search
        elif any(cmd.startswith(x + " ") for x in ["examine", "search"]):
            obj_name = cmd.split(" ", 1)[1]
            obj = next((o for o in self.inventory if o.name.lower() == obj_name), None)
            if not obj:
                room = (
                    self.rooms.get(self.current_room)
                    if self.current_room and self.current_room in self.rooms
                    else None
                )
                if room:
                    obj = next(
                        (o for o in room.objects if o.name.lower() == obj_name), None
                    )
            if obj:
                print(f"{obj.name}: {obj.description}")
            else:
                print(f"You see no {obj_name} to examine.")
            return True
        # Take all command
        elif cmd in ["take all", "get all"]:
            room = (
                self.rooms.get(self.current_room)
                if self.current_room and self.current_room in self.rooms
                else None
            )
            if not room or not room.objects:
                print("There is nothing here to take.")
                return True
            taken_any = False
            for obj in list(room.objects):
                if (
                    self.get_inventory_weight() + getattr(obj, "osize", 1)
                    > self.LOAD_MAX
                ):
                    print(
                        f"You can't carry the {obj.name}; it's too heavy or you're overloaded."
                    )
                    continue
                self.inventory.append(obj)
                room.objects.remove(obj)
                print(f"You take the {obj.name}.")
                taken_any = True
            if not taken_any:
                print("You couldn't take anything.")
            return True
        # Basic stubs for other commands
        elif cmd in ["get", "take"]:
            print("Specify what to take, e.g. 'get mat'.")
            return True
        elif cmd in ["drop", "put", "throw"]:
            print("Specify what to drop, e.g. 'drop mat'.")
            return True
        elif cmd in ["climb", "jump", "swim"] or any(
            cmd.startswith(x + " ") for x in ["climb", "jump", "swim"]
        ):
            print("[Stub] You try to climb/jump/swim.")
            return True
        elif cmd in ["attack"] or cmd.startswith("attack "):
            print("[Stub] You try to attack.")
            return True
        elif cmd in ["help"]:
            print(
                "[Stub] Help: Available commands are look, go, inventory, get, drop, open, close, read, eat, drink, climb, jump, swim, attack, help, save, restore, restart, score, wait, listen, examine, search, unlock, lock, turn, push, pull, light, extinguish, wear, remove, quit."
            )
            return True
        elif cmd in ["save"]:
            self.save_game()
            return True
        elif cmd in ["restore", "load"]:
            self.load_game()
            return True
        elif cmd in ["restart"]:
            print("Restarting game...")
            self.__init__()
            self.describe_current_room()
            return True
        elif cmd in ["score"]:
            print(f"Your score is {self.score}.")
            return True
        elif cmd in ["wait"]:
            print("[Stub] You wait a moment.")
            return True
        elif cmd in ["listen"]:
            print("[Stub] You listen carefully.")
            return True
        elif cmd in ["unlock", "lock"] or any(
            cmd.startswith(x + " ") for x in ["unlock", "lock"]
        ):
            print("[Stub] You try to unlock/lock something.")
            return True
        elif cmd in ["turn", "push", "pull"] or any(
            cmd.startswith(x + " ") for x in ["turn", "push", "pull"]
        ):
            print("[Stub] You try to turn/push/pull something.")
            return True
        elif cmd in ["light", "extinguish"] or any(
            cmd.startswith(x + " ") for x in ["light", "extinguish"]
        ):
            print("[Stub] You try to light/extinguish something.")
            return True
        elif cmd in ["wear", "remove"] or any(
            cmd.startswith(x + " ") for x in ["wear", "remove"]
        ):
            print("[Stub] You try to wear/remove something.")
            return True
        else:
            print(
                "Unknown command. Try 'look', 'go <direction>', 'inventory', or 'quit'."
            )
            return True


if __name__ == "__main__":
    import sys

    demo_mode = False
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode = True
    print(
        "Welcome to Phork! Type 'look' to see your surroundings, 'go <direction>' to move, 'inventory' to check your items, or 'quit' to exit."
    )
    if demo_mode:
        print(
            "[Demo Mode Enabled] Carry limits are disabled and all starting objects are in your inventory."
        )
    game = Game(demo_mode=demo_mode)
    game.describe_current_room()
    while True:
        command = input("\n> ")
        if not game.parse_command(command):
            break
