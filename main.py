from entities import Room, Player, Action, THIEF, TROLL, CYCLOPS, GRUE, ROBOT
from puzzles import trigger_puzzle
from objects import GameObject
from containers import Container
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
        # Add canonical NPCs to their rooms
        rooms["WHOUS"] = Room(
            id="WHOUS",
            desc_long=(
                "West of House\n\n"
                "You are standing in an open field west of a white house, with a boarded front door.\n"
                "There is a small mailbox here."
            ),
            desc_short="West of House",
            exits={"east": "HOUSE"},
            objects=[
                GameObject(
                    "Welcome Mat",
                    "A simple mat lies here.",
                    attributes={
                        "osize": 1,
                        "score_value": 0,
                        "takeable": True,
                        "portable": True,
                    },
                ),
                GameObject(
                    "Lantern",
                    "A brass lantern, unlit.",
                    attributes={
                        "osize": 2,
                        "score_value": 0,
                        "lit": False,
                        "takeable": True,
                        "portable": True,
                    },
                ),
                GameObject(
                    "Sword",
                    "A sharp sword gleams here.",
                    attributes={
                        "osize": 3,
                        "score_value": 0,
                        "weapon": True,
                        "takeable": True,
                        "portable": True,
                    },
                ),
                Container(
                    "Mailbox",
                    "A small mailbox. It is closed.",
                    attributes={
                        "osize": 4,
                        "open": False,
                        "openable": True,
                        "locked": True,
                        "container": True,
                        "takeable": False,
                        "portable": False,
                        "contents": [
                            GameObject(
                                "Leaflet",
                                (
                                    "WELCOME TO PHORK\n\n"
                                    "PHORK is a game of adventure, danger, and low cunning. In it you will explore some of the most amazing territory ever seen by mortal man. "
                                    "Hardened adventurers have run screaming from the terrors contained within!\n\n"
                                    "No computer should be without one!"
                                ),
                                attributes={
                                    "osize": 1,
                                    "score_value": 0,
                                    "readable": True,
                                    "takeable": True,
                                    "portable": True,
                                },
                            )
                        ],
                    },
                ),
                GameObject(
                    "Key",
                    "A small key.",
                    attributes={
                        "osize": 1,
                        "score_value": 0,
                        "takeable": True,
                        "portable": True,
                    },
                ),
                GameObject(
                    "Treasure Chest",
                    "A heavy chest, locked.",
                    attributes={
                        "osize": 10,
                        "score_value": 15,
                        "locked": True,
                        "openable": True,
                        "container": True,
                        "takeable": False,
                        "portable": False,
                    },
                ),
            ],
            flags=[],
            action=None,
            npcs=[],  # THIEF will be added in demo mode only
        )
        # Set locked exit for WHOUS
        rooms["WHOUS"].locked_exits = {"east": True}
        # Canonical locked objects
        for obj in rooms["WHOUS"].objects:
            if obj.name.lower() == "treasure chest":
                obj.attributes["locked"] = True
            if obj.name.lower() == "mailbox":
                obj.attributes["locked"] = True
        # Add locked exit for HOUSE west door (for symmetry)
        rooms["HOUSE"] = Room(
            id="HOUSE",
            desc_long="You are inside the white house. There is a door to the west.",
            desc_short="Inside House",
            exits={"west": "WHOUS"},
            objects=[
                GameObject(
                    "Painting",
                    "A beautiful painting hangs on the wall.",
                    attributes={
                        "osize": 5,
                        "score_value": 10,
                        "takeable": False,
                        "portable": False,
                        "hangable": True,
                    },
                ),
                GameObject(
                    "Table",
                    "A wooden table stands here.",
                    attributes={
                        "osize": 8,
                        "score_value": 0,
                        "takeable": False,
                        "portable": False,
                        "surface": True,
                    },
                ),
            ],
            flags=[],
            action=None,
            npcs=[TROLL, CYCLOPS, ROBOT],
        )
        # Add canonical NPCs to their rooms
        rooms["TROLL"] = Room(
            id="TROLL",
            desc_long="A menacing troll blocks the bridge, demanding payment.",
            desc_short="Troll Room",
            exits={"north": "BRIDGE", "south": "CELLA"},
            objects=[
                GameObject("Axe", "A heavy troll's axe.", attributes={"osize": 5})
            ],
            flags=[],
            action=None,
            npcs=[TROLL],
        )
        rooms["CYCLO"] = Room(
            id="CYCLO",
            desc_long="A huge cyclops glares at you, hungry and irritable.",
            desc_short="Cyclops Room",
            exits={"down": "TROLL"},
            objects=[],
            flags=[],
            action=None,
            npcs=[CYCLOPS],
        )
        rooms["TREAS"] = Room(
            id="TREAS",
            desc_long="The Treasure Room sparkles with loot. A sneaky thief lurks here, eyeing your valuables.",
            desc_short="Treasure Room",
            exits={"west": "CYCLO"},
            objects=[
                GameObject(
                    "Chalice",
                    "A golden chalice encrusted with gems.",
                    attributes={"osize": 2, "score_value": 25},
                )
            ],
            flags=[],
            action=None,
            npcs=[THIEF],
        )
        # Add Robot to Maintenance Room if present
        if "MAINT" in rooms:
            rooms["MAINT"].npcs.append(ROBOT)
    return rooms


class Game:
    def handle_death(self):
        print("It appears that that last blow was too much for you. You are dead.")
        while True:
            choice = (
                input("Would you like to restart, restore, or quit? ").strip().lower()
            )
            if choice == "restart":
                self.restart_game()
                break
            elif choice == "restore":
                self.load_game()
                break
            elif choice == "quit":
                print("Thanks for playing!")
                exit()
            else:
                print("Please type 'restart', 'restore', or 'quit'.")

    def restart_game(self):
        demo_mode = getattr(self, "demo_mode", False)
        self.__init__(demo_mode=demo_mode)
        print("Game restarted. Good luck!")

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
                print(GRUE.description)
            elif self.dark_moves >= 2:
                print(GRUE.interact(self))
                exit()
        else:
            self.dark_moves = 0  # Reset counter if not in darkness

    def __init__(self, demo_mode=False):
        import random

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
        self.thief_room = (
            "WHOUS" if self.demo_mode else None
        )  # Track Thief's current room
        self.thief_visible = False  # Is Thief currently visible to player?
        self.thief_cooldown = 0  # Moves until next possible encounter
        from entities import Player

        start_room = (
            self.current_room
            if isinstance(self.current_room, str) and self.current_room
            else "WHOUS"
        )
        self.player = Player("Adventurer", start_room)
        if self.demo_mode:
            # Always add all canonical NPCs to WHOUS in demo mode, regardless of how it was loaded
            whous = self.rooms.get("WHOUS")
            if whous:
                if not hasattr(whous, "npcs") or whous.npcs is None:
                    whous.npcs = []
                for npc in [THIEF, TROLL, CYCLOPS, GRUE, ROBOT]:
                    if npc not in whous.npcs:
                        whous.npcs.append(npc)
            # Give player all non-container objects from starting room, ignore carry limit
            room = self.rooms.get(self.current_room)
            if room and room.objects:
                non_containers = [
                    o for o in room.objects if not o.attributes.get("container")
                ]
                self.inventory.extend(non_containers)
                room.objects = [
                    o for o in room.objects if o.attributes.get("container")
                ]
            print(
                "[Demo Mode] All non-container objects have been added to your inventory. Carry limits are disabled."
            )

    def tick_thief(self):
        import random

        # Only run if Thief is enabled (demo or canonical rooms)
        if self.thief_room is None:
            return
        # Thief moves randomly between rooms
        room_ids = list(self.rooms.keys())
        # Thief should not move to rooms with 'dark' or 'locked' flags
        valid_rooms = [
            rid
            for rid in room_ids
            if "dark" not in getattr(self.rooms[rid], "flags", [])
            and "locked" not in getattr(self.rooms[rid], "flags", [])
        ]
        if not valid_rooms:
            valid_rooms = room_ids
        # Move thief every tick
        self.thief_room = random.choice(valid_rooms)
        # Thief may appear in player's room
        self.thief_visible = (
            self.thief_room == self.current_room and random.random() < 0.4
        )
        # Thief cooldown for next encounter
        self.thief_cooldown = random.randint(2, 5)
        # Add/remove thief from room NPCs
        for rid, room in self.rooms.items():
            if hasattr(room, "npcs"):
                if THIEF in room.npcs:
                    room.npcs.remove(THIEF)
        if self.thief_visible:
            room = self.rooms.get(self.current_room)
            if room and hasattr(room, "npcs") and THIEF not in room.npcs:
                room.npcs.append(THIEF)

    def maybe_thief_event(self):
        import random

        # Only run if Thief is visible
        if not self.thief_visible:
            return
        # Canonical random events: steal, attack, vanish
        event = random.choices(
            ["steal", "attack", "vanish", "ignore"], weights=[0.5, 0.2, 0.2, 0.1]
        )[0]
        if event == "steal" and self.inventory:
            item = random.choice(self.inventory)
            self.inventory.remove(item)
            print(f"The thief snatches your {item.name} and vanishes!")
            self.thief_visible = False
            self.thief_room = None
        elif event == "attack":
            print("The thief suddenly attacks! You barely dodge his blade.")
        elif event == "vanish":
            print("The thief vanishes into the shadows!")
            self.thief_visible = False
            self.thief_room = None
        elif event == "ignore":
            print("The thief eyes you but does nothing.")

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
            "player": self.player,
            "thief_room": self.thief_room,
            "thief_visible": self.thief_visible,
            "thief_cooldown": self.thief_cooldown,
            "demo_mode": self.demo_mode,
            "mailbox_open": self.mailbox_open,
            "leaflet_taken": self.leaflet_taken,
            "lantern_lit": self.lantern_lit,
            "dark_moves": self.dark_moves,
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
            self.player = state.get("player", self.player)
            self.thief_room = state.get("thief_room", self.thief_room)
            self.thief_visible = state.get("thief_visible", self.thief_visible)
            self.thief_cooldown = state.get("thief_cooldown", self.thief_cooldown)
            self.demo_mode = state.get("demo_mode", self.demo_mode)
            self.mailbox_open = state.get("mailbox_open", self.mailbox_open)
            self.leaflet_taken = state.get("leaflet_taken", self.leaflet_taken)
            self.lantern_lit = state.get("lantern_lit", self.lantern_lit)
            self.dark_moves = state.get("dark_moves", self.dark_moves)
            print(f"Game loaded from {filename}.")
            self.describe_current_room()
        except Exception as e:
            print(f"Error loading game: {e}")

    def check_room_flags(self):
        room = self.rooms.get(self.current_room)
        if not room:
            return
        # Example: handle dark rooms
        if "dark" in getattr(room, "flags", []):
            print("It is pitch dark. You are likely to be eaten by a grue.")
        # Example: handle locked rooms
        if "locked" in getattr(room, "flags", []):
            print("The room is locked.")
        # Add more flag logic as needed
        if self.check_grue_danger():
            exit()

    def check_puzzles(self):
        # Example: check if a puzzle in the current room is solved
        puzzle_key = f"{self.current_room}_puzzle"
        if self.puzzles.get(puzzle_key):
            if not self.puzzles.get(f"{puzzle_key}_scored"):
                self.score += 5  # Award points for solving a puzzle
                self.puzzles[f"{puzzle_key}_scored"] = True
                print("You have solved the puzzle in this room! (+5 points)")
            else:
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
        # Show all visible objects, including containers and their contents if open
        demo_object_names = {
            "welcome mat",
            "lantern",
            "sword",
            "key",
            "robot",
            "treasure chest",
        }
        objects_to_print = []
        containers_to_print = []
        for obj in room.objects:
            if not self.demo_mode and obj.name.lower() in demo_object_names:
                continue
            if hasattr(obj, "is_container") and obj.is_container():
                containers_to_print.append(obj)
            else:
                objects_to_print.append(obj)
        # Show NPCs present in the room
        if hasattr(room, "npcs") and room.npcs:
            print("You see:")
            for npc in room.npcs:
                print(f"  {npc.name}: {npc.description}")
        # Print objects and container contents only once
        if objects_to_print or containers_to_print:
            print("Objects:")
            for obj in objects_to_print:
                if obj.name.lower() == "leaflet":
                    print(f"  {obj.name}: There is a small leaflet here.")
                else:
                    print(f"  {obj.name}: {obj.description}")
            for container in containers_to_print:
                print(f"  {container.name}: {container.description}")
                if container.attributes.get("open", False):
                    for item in container.attributes.get("contents", []):
                        if item.name.lower() == "leaflet":
                            print(
                                f"    {item.name} (in {container.name}): There is a small leaflet here."
                            )
                        else:
                            print(
                                f"    {item.name} (in {container.name}): {item.description}"
                            )

    def move(self, direction):
        if not self.current_room or self.current_room not in self.rooms:
            print("No valid current room.")
            return
        room = self.rooms[self.current_room]
        # Check for locked exits
        locked_exits = getattr(room, "locked_exits", {})
        if direction in locked_exits and locked_exits[direction]:
            print(f"The door to {direction} is locked.")
            return
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

    def unlock_exit(self, direction):
        room = self.rooms[self.current_room]
        locked_exits = getattr(room, "locked_exits", {})
        if direction in locked_exits and locked_exits[direction]:
            # Check for key in inventory
            has_key = any(obj.name.lower() == "key" for obj in self.inventory)
            if has_key:
                locked_exits[direction] = False
                print(f"You unlock the door to {direction} with your key.")
            else:
                print("You need a key to unlock this door.")
        else:
            print(f"There is no locked door to {direction} here.")

    def lock_exit(self, direction):
        room = self.rooms[self.current_room]
        locked_exits = getattr(room, "locked_exits", {})
        if direction in room.exits:
            locked_exits[direction] = True
            print(f"You lock the door to {direction}.")
        else:
            print(f"There is no door to {direction} here.")

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
        # Thief random encounter tick
        if self.thief_cooldown > 0:
            self.thief_cooldown -= 1
        else:
            self.tick_thief()
        self.maybe_thief_event()
        cmd = command.strip().lower()
        # Canonical: put <item> in <container>
        if cmd.startswith("put ") and " in " in cmd:
            parts = cmd.split(" in ", 1)
            item_name = parts[0][4:].strip()
            container_name = parts[1].strip()
            item = next(
                (o for o in self.inventory if o.name.lower() == item_name), None
            )
            room = self.rooms.get(self.current_room)
            container = None
            if room:
                container = next(
                    (
                        o
                        for o in room.objects
                        if hasattr(o, "is_container")
                        and o.is_container()
                        and o.name.lower() == container_name
                    ),
                    None,
                )
            if not item:
                print(f"You don't have a {item_name} to put.")
                return True
            if not container:
                print(f"There is no {container_name} here to put things in.")
                return True
            if not container.attributes.get("open", False):
                print(f"The {container.name} is closed.")
                return True
            self.inventory.remove(item)
            container.attributes.setdefault("contents", []).append(item)
            print(f"You put the {item.name} in the {container.name}.")
            return True
        # Canonical: place <item> on <surface>
        if cmd.startswith("place ") and " on " in cmd:
            parts = cmd.split(" on ", 1)
            item_name = parts[0][6:].strip()
            surface_name = parts[1].strip()
            item = next(
                (o for o in self.inventory if o.name.lower() == item_name), None
            )
            room = self.rooms.get(self.current_room)
            surface = None
            if room:
                surface = next(
                    (
                        o
                        for o in room.objects
                        if o.name.lower() == surface_name
                        and o.attributes.get("surface", False)
                    ),
                    None,
                )
            if not item:
                print(f"You don't have a {item_name} to place.")
                return True
            if not surface:
                print(f"There is no {surface_name} here to place things on.")
                return True
            self.inventory.remove(item)
            room.objects.append(item)
            print(f"You place the {item.name} on the {surface.name}.")
            return True
        # Canonical: unlock <container> with <key>
        if cmd.startswith("unlock ") and " with " in cmd:
            parts = cmd.split(" with ", 1)
            container_name = parts[0][7:].strip()
            key_name = parts[1].strip()
            room = self.rooms.get(self.current_room)
            container = None
            if room:
                container = next(
                    (
                        o
                        for o in room.objects
                        if hasattr(o, "is_container")
                        and o.is_container()
                        and o.name.lower() == container_name
                    ),
                    None,
                )
            key = next((o for o in self.inventory if o.name.lower() == key_name), None)
            if not container:
                print(f"There is no {container_name} here to unlock.")
                return True
            if not key:
                print(f"You don't have a {key_name} to unlock the {container_name}.")
                return True
            if not container.attributes.get("locked", False):
                print(f"The {container.name} is already unlocked.")
                return True
            container.attributes["locked"] = False
            container.attributes["open"] = True
            print(f"You unlock the {container.name} with the {key.name}.")
            return True
        # Canonical: lock <container>
        if cmd.startswith("lock "):
            container_name = cmd[5:].strip()
            room = self.rooms.get(self.current_room)
            container = None
            if room:
                container = next(
                    (
                        o
                        for o in room.objects
                        if hasattr(o, "is_container")
                        and o.is_container()
                        and o.name.lower() == container_name
                    ),
                    None,
                )
            if not container:
                # Fall back to exit locking
                pass
            elif not container.attributes.get("openable", False):
                print(f"The {container.name} cannot be locked.")
                return True
            elif container.attributes.get("locked", False):
                print(f"The {container.name} is already locked.")
                return True
            else:
                container.attributes["locked"] = True
                container.attributes["open"] = False
                print(f"You lock the {container.name}.")
                return True
        # Canonical: tie <object> to <object>
        if cmd.startswith("tie ") and " to " in cmd:
            parts = cmd.split(" to ", 1)
            obj1_name = parts[0][4:].strip()
            obj2_name = parts[1].strip()
            obj1 = next(
                (o for o in self.inventory if o.name.lower() == obj1_name), None
            )
            room = self.rooms.get(self.current_room)
            obj2 = None
            if room:
                obj2 = next(
                    (o for o in room.objects if o.name.lower() == obj2_name), None
                )
            if not obj1:
                print(f"You don't have a {obj1_name} to tie.")
                return True
            if not obj2:
                print(f"There is no {obj2_name} here to tie things to.")
                return True
            print(
                f"You tie the {obj1.name} to the {obj2.name}. (Nothing special happens.)"
            )
            return True
        # Canonical: turn <object>
        if cmd.startswith("turn "):
            obj_name = cmd[5:].strip()
            room = self.rooms.get(self.current_room)
            obj = None
            if room:
                obj = next(
                    (o for o in room.objects if o.name.lower() == obj_name), None
                )
            if not obj:
                print(f"There is no {obj_name} here to turn.")
                return True
            print(f"You turn the {obj.name}. Nothing happens.")
            return True
        # Canonical: search <container> or room
        if cmd.startswith("search "):
            obj_name = cmd[7:].strip()
            room = self.rooms.get(self.current_room)
            obj = None
            if room:
                obj = next(
                    (
                        o
                        for o in room.objects
                        if o.name.lower() == obj_name
                        and hasattr(o, "is_container")
                        and o.is_container()
                    ),
                    None,
                )
            if obj:
                if obj.attributes.get("open", False):
                    contents = obj.attributes.get("contents", [])
                    if contents:
                        print(f"You search the {obj.name} and find:")
                        for item in contents:
                            print(f"  {item.name}: {item.description}")
                    else:
                        print(f"You search the {obj.name} but find nothing inside.")
                else:
                    print(f"The {obj.name} is closed.")
                return True
            # If not a container, search the room
            if obj_name in [room.id.lower(), "room", "area"]:
                found = False
                for o in room.objects:
                    if (
                        hasattr(o, "is_container")
                        and o.is_container()
                        and o.attributes.get("open", False)
                    ):
                        contents = o.attributes.get("contents", [])
                        if contents:
                            print(f"You search the {o.name} and find:")
                            for item in contents:
                                print(f"  {item.name}: {item.description}")
                            found = True
                if not found:
                    print("You search the room but find nothing special.")
                return True
            print(f"You find nothing special about the {obj_name}.")
            return True

        # Object interaction: push/pull
        if any(cmd.startswith(x + " ") for x in ["push", "pull"]):
            obj_name = cmd.split(" ", 1)[1]
            snarky_pushpull = [
                "Nothing happens.",
                "You must be joking.",
                "Pushing and pulling accomplishes nothing.",
                "That doesn't seem to work.",
                "You can't {verb} the {name}.",
            ]
            verb = cmd.split(" ")[0]
            print(
                snarky_pushpull[-1].format(verb=verb, name=obj_name)
                if verb in ["push", "pull"]
                else random.choice(snarky_pushpull)
            )
            return True

        # Object interaction: use
        if cmd.startswith("use "):
            obj_name = cmd.split(" ", 1)[1]
            snarky_use = [
                "You can't use that here.",
                "Nothing happens.",
                "Use the {name}? How?",
                "You must be joking.",
            ]
            print(random.choice(snarky_use).format(name=obj_name))
            return True

        # Object interaction: hang/place
        if any(cmd.startswith(x + " ") for x in ["hang", "place"]):
            obj_name = cmd.split(" ", 1)[1]
            snarky_hangplace = [
                "You can't do that.",
                "There's nowhere to hang the {name}.",
                "Placing the {name} accomplishes nothing.",
                "You must be joking.",
            ]
            print(random.choice(snarky_hangplace).format(name=obj_name))
            return True

        # Object interaction: examine (synonym for look)
        if cmd.startswith("examine "):
            obj_name = cmd.split(" ", 1)[1]
            from object_actions import object_action

            if object_action(self, "look", obj_name):
                return True
            print(f"You see nothing special about the {obj_name}.")
            return True
        # Canonical NPC interactions
        # Modular two-way combat for attack/fight/kill/stab/hit
        combat_actions = ["fight ", "attack ", "kill ", "stab ", "hit "]
        for prefix in combat_actions:
            if cmd.startswith(prefix):
                npc_name = cmd[len(prefix) :].strip()
                room = self.rooms.get(self.current_room)
                npc = next(
                    (
                        n
                        for n in getattr(room, "npcs", [])
                        if n.name.lower() == npc_name
                    ),
                    None,
                )
                if npc:
                    from combat import CombatEngine

                    print(CombatEngine.combat_round(self.player, npc))
                    if self.player.is_dead():
                        self.handle_death()
                        return True
                else:
                    print(f"There is no {npc_name} here to attack.")
                return True
        # Other NPC interactions
        npc_actions = [
            ("talk ", "talk"),
            ("greet ", "greet"),
            ("hello ", "hello"),
            ("poke ", "poke"),
            ("tie ", "tie"),
        ]
        for prefix, action in npc_actions:
            if cmd.startswith(prefix):
                npc_name = cmd[len(prefix) :].strip()
                room = self.rooms.get(self.current_room)
                npc = next(
                    (
                        n
                        for n in getattr(room, "npcs", [])
                        if n.name.lower() == npc_name
                    ),
                    None,
                )
                if npc:
                    print(npc.interact(self, action=action))
                else:
                    print(f"There is no {npc_name} here to {action}.")
                return True
        # Check for player death after any command
        if self.player.is_dead():
            self.handle_death()
            return True
        # Give <item> <npc>
        if cmd.startswith("give "):
            parts = cmd.split(" ")
            if len(parts) == 3:
                item_name, npc_name = parts[1], parts[2]
                item = next(
                    (o for o in self.inventory if o.name.lower() == item_name), None
                )
                room = self.rooms.get(self.current_room)
                npc = next(
                    (
                        n
                        for n in getattr(room, "npcs", [])
                        if n.name.lower() == npc_name
                    ),
                    None,
                )
                if npc and item:
                    print(npc.interact(self, action="give", item=item))
                    self.inventory.remove(item)
                else:
                    print("Give failed: check NPC and item names.")
            else:
                print("Usage: give <item> <npc>")
            return True
        # Bribe <npc> <item>
        if cmd.startswith("bribe "):
            parts = cmd.split(" ")
            if len(parts) == 3:
                npc_name, item_name = parts[1], parts[2]
                item = next(
                    (o for o in self.inventory if o.name.lower() == item_name), None
                )
                room = self.rooms.get(self.current_room)
                npc = next(
                    (
                        n
                        for n in getattr(room, "npcs", [])
                        if n.name.lower() == npc_name
                    ),
                    None,
                )
                if npc and item:
                    print(npc.interact(self, action="bribe", item=item))
                    self.inventory.remove(item)
                else:
                    print("Bribe failed: check NPC and item names.")
            else:
                print("Usage: bribe <npc> <item>")
            return True
        # Canonical commands from MUD source
        if cmd in ["quit", "exit"]:
            print("Thanks for playing!")
            return False
        elif cmd in ["look", "l"]:
            self.look()
            return True
        # Cardinal direction short commands
        cardinal_map = {
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            "ne": "northeast",
            "nw": "northwest",
            "se": "southeast",
            "sw": "southwest",
            "u": "up",
            "d": "down",
        }
        cardinal_dirs = list(cardinal_map.keys()) + ["up", "down"]
        if cmd in cardinal_dirs:
            direction = cardinal_map.get(cmd, cmd)
            room = self.rooms[self.current_room]
            locked_exits = getattr(room, "locked_exits", {})
            if direction in locked_exits and locked_exits[direction]:
                print(f"The door to {direction} is locked.")
        elif (
            self.current_room
            and self.current_room in self.rooms
            and cmd in self.rooms[self.current_room].exits
        ):
            direction = cardinal_map.get(cmd, cmd)
            room = self.rooms[self.current_room]
            locked_exits = getattr(room, "locked_exits", {})
            if direction in locked_exits and locked_exits[direction]:
                print(f"The door to {direction} is locked.")
                return True
            self.move(direction)
            return True
        elif (
            self.current_room
            and self.current_room in self.rooms
            and cmd in self.rooms[self.current_room].exits
        ):
            room = self.rooms[self.current_room]
            locked_exits = getattr(room, "locked_exits", {})
            if cmd in locked_exits and locked_exits[cmd]:
                print(f"The door to {cmd} is locked.")
                return True
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
            # Check for 'take all' first
            if obj_name == "all":
                if not room or not room.objects:
                    print("There is nothing here to take.")
                    return True
                taken_any = False
                for obj in list(room.objects):
                    # Prevent taking leaflet unless mailbox is open
                    if obj.name.lower() == "leaflet":
                        # Check containers for leaflet
                        mailbox = next(
                            (
                                o
                                for o in room.objects
                                if hasattr(o, "is_container")
                                and o.is_container()
                                and o.name.lower() == "mailbox"
                            ),
                            None,
                        )
                        if mailbox and mailbox.attributes.get("open", False):
                            contents = mailbox.attributes.get("contents", [])
                            leaflet_obj = next(
                                (o for o in contents if o.name.lower() == "leaflet"),
                                None,
                            )
                            if leaflet_obj:
                                mailbox.remove_object(leaflet_obj)
                                self.inventory.append(leaflet_obj)
                                print("You take the leaflet.")
                                taken_any = True
                                continue
                        print("You can't take the leaflet unless the mailbox is open.")
                        continue
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
                # Also check open containers for takeable objects
                for obj in room.objects:
                    if (
                        hasattr(obj, "is_container")
                        and obj.is_container()
                        and obj.attributes.get("open", False)
                    ):
                        for item in list(obj.attributes.get("contents", [])):
                            obj_weight = (
                                item.attributes.get("osize")
                                if hasattr(item, "attributes")
                                and "osize" in item.attributes
                                else getattr(item, "osize", 1)
                            )
                            if obj_weight == self.BIGFIX:
                                obj_weight = 0
                            if (
                                not self.demo_mode
                                and self.get_inventory_weight() + obj_weight
                                > self.LOAD_MAX
                            ):
                                print(
                                    f"You can't carry the {item.name}; it's too heavy or you're overloaded."
                                )
                                continue
                            obj.remove_object(item)
                            self.inventory.append(item)
                            print(f"You take the {item.name} from the {obj.name}.")
                            taken_any = True
                if not taken_any:
                    print("You couldn't take anything.")
                return True
            if room:
                # First, check all visible objects (case-insensitive, robust)
                def normalize(s):
                    return " ".join(s.lower().split())

                obj_name_norm = normalize(obj_name)
                # Gather all objects in room, including all containers (open or closed) and their contents if open
                all_objs = []
                for obj in room.objects:
                    all_objs.append(obj)  # Always include the object itself
                    if hasattr(obj, "is_container") and obj.is_container():
                        if obj.attributes.get("open", False):
                            all_objs.extend(obj.attributes.get("contents", []))
                print(
                    f"[DEBUG] take/get: obj_name='{obj_name}', normalized='{obj_name_norm}'"
                )
                print(f"[DEBUG] Objects considered:")
                for o in all_objs:
                    print(
                        f"  - {o.name} (normalized: '{normalize(o.name)}', type: {type(o)})"
                    )
                # Try exact match
                obj = next(
                    (o for o in all_objs if normalize(o.name) == obj_name_norm), None
                )
                # Try partial match
                if not obj:
                    obj = next(
                        (o for o in all_objs if obj_name_norm in normalize(o.name)),
                        None,
                    )
                # Try aliases if present
                if not obj:
                    obj = next(
                        (
                            o
                            for o in all_objs
                            if hasattr(o, "aliases")
                            and any(
                                obj_name_norm == normalize(alias) for alias in o.aliases
                            )
                        ),
                        None,
                    )
                if obj:
                    # Prevent taking leaflet unless mailbox is open
                    if obj.name.lower() == "leaflet":
                        mailbox = next(
                            (
                                o
                                for o in room.objects
                                if hasattr(o, "is_container")
                                and o.is_container()
                                and o.name.lower() == "mailbox"
                            ),
                            None,
                        )
                        if mailbox and mailbox.attributes.get("open", False):
                            contents = mailbox.attributes.get("contents", [])
                            leaflet_obj = next(
                                (o for o in contents if o.name.lower() == "leaflet"),
                                None,
                            )
                            if leaflet_obj:
                                mailbox.remove_object(leaflet_obj)
                                self.inventory.append(leaflet_obj)
                                print("You take the leaflet.")
                                return True
                        print("You can't take the leaflet unless the mailbox is open.")
                        return True
                    # Canonical snarky responses for uncarryable objects
                    if not obj.attributes.get(
                        "takeable", True
                    ) or not obj.attributes.get("portable", True):
                        snarky_lines = [
                            "The {name} is an integral part of the scenery and cannot be taken.",
                            "You must be joking.",
                            "That's hardly portable.",
                            "You can't be serious.",
                            "You can't take that.",
                        ]
                        import random

                        print(random.choice(snarky_lines).format(name=obj.name))
                        return True
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
                    if obj.name.lower() in [
                        "treasure chest",
                        "treasure",
                        "jewel",
                        "gold",
                        "diamond",
                    ]:
                        self.score += 10  # Award points for treasures
                        print("You have found a treasure! (+10 points)")
                    else:
                        self.score += 1  # Minor score for other items
                    return True
                # Next, check open containers for the object
                for container in room.objects:
                    if (
                        hasattr(container, "is_container")
                        and container.is_container()
                        and container.attributes.get("open", False)
                    ):
                        item = next(
                            (
                                o
                                for o in container.attributes.get("contents", [])
                                if o.name.lower() == obj_name
                            ),
                            None,
                        )
                        if item:
                            obj_weight = (
                                item.attributes.get("osize")
                                if hasattr(item, "attributes")
                                and "osize" in item.attributes
                                else getattr(item, "osize", 1)
                            )
                            if obj_weight == self.BIGFIX:
                                obj_weight = 0
                            if (
                                not self.demo_mode
                                and self.get_inventory_weight() + obj_weight
                                > self.LOAD_MAX
                            ):
                                print(
                                    f"You cannot carry the {item.name}. Your load is too heavy."
                                )
                                return True
                            container.remove_object(item)
                            self.inventory.append(item)
                            print(
                                f"You take the {item.name} from the {container.name}."
                            )
                            self.score += 1
                            return True
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
            # Gather all objects in room and inventory
            room = self.rooms.get(self.current_room)
            all_objs = []
            if room:
                for obj in room.objects:
                    all_objs.append(obj)
                    if (
                        hasattr(obj, "is_container")
                        and obj.is_container()
                        and obj.attributes.get("open", False)
                    ):
                        all_objs.extend(obj.attributes.get("contents", []))
            all_objs.extend(self.inventory)

            def normalize(s):
                return " ".join(s.lower().split())

            obj_name_norm = normalize(obj_name)
            obj = next(
                (o for o in all_objs if normalize(o.name) == obj_name_norm), None
            )
            if obj:
                # Canonical snark for non-edible objects
                if not obj.attributes.get("edible", False):
                    snarky_eat = [
                        "I don't think that would be very tasty.",
                        "You must be joking.",
                        "Eat the {name}? Really?",
                        "That's not edible.",
                        "You can't eat that.",
                    ]
                    import random

                    print(random.choice(snarky_eat).format(name=obj.name))
                    return True
                else:
                    print(f"You eat the {obj.name}.")
                    self.inventory.remove(obj)
                    self.score += 1
                    return True
            print(f"There is no {obj_name} here to {cmd.split(' ')[0]}.")
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
        # Object interaction: unlock/lock exits with smart direction handling
        elif cmd.startswith("unlock "):
            arg = cmd.split(" ", 1)[1]
            room = self.rooms[self.current_room]
            locked_exits = getattr(room, "locked_exits", {})
            locked_doors = [d for d, locked in locked_exits.items() if locked]
            if arg in locked_exits:
                self.unlock_exit(arg)
            elif arg in ["door", "doors"]:
                if len(locked_doors) == 1:
                    self.unlock_exit(locked_doors[0])
                elif len(locked_doors) > 1:
                    print(
                        f"Which door do you want to unlock? Locked doors: {', '.join(locked_doors)}."
                    )
                else:
                    print("There are no locked doors here.")
            else:
                print(f"Unknown door or direction '{arg}'.")
            return True
        elif cmd.startswith("lock "):
            arg = cmd.split(" ", 1)[1]
            room = self.rooms[self.current_room]
            unlocked_doors = [
                d
                for d in room.exits
                if not getattr(room, "locked_exits", {}).get(d, False)
            ]
            if arg in room.exits:
                self.lock_exit(arg)
            elif arg in ["door", "doors"]:
                if len(unlocked_doors) == 1:
                    self.lock_exit(unlocked_doors[0])
                elif len(unlocked_doors) > 1:
                    print(
                        f"Which door do you want to lock? Unlocked doors: {', '.join(unlocked_doors)}."
                    )
                else:
                    print("There are no unlocked doors here.")
            else:
                print(f"Unknown door or direction '{arg}'.")
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
        elif cmd.startswith("unlock "):
            direction = cmd.split(" ", 1)[1]
            self.unlock_exit(direction)
            return True
        elif cmd.startswith("lock "):
            direction = cmd.split(" ", 1)[1]
            self.lock_exit(direction)
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
