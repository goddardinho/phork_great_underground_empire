from load_rooms import load_rooms
from entities import Room, Player, Action, THIEF, TROLL, CYCLOPS, GRUE, ROBOT
from puzzles import trigger_puzzle
from objects import GameObject
from containers import Container
from parsers import parse_exits, parse_objects, parse_flags, parse_action
import re
import pickle
import random
from help_utils import show_help

BIGFIX = 9999  # Canonical value for uncarryable objects
LOAD_MAX = 10  # Canonical Zork I carry limit (adjust as needed)


class Game:

    def handle_death(self):
        """Handle player death by invoking the game over sequence."""
        self.game_over()

    # No stray flags assignment here
    def is_room_dark(self, room_id=None):
        room = self.rooms.get(room_id or self.current_room)
        if not room:
            return False
        # Room is dark if it has the ROOM_DARK flag and no light source is present
        if room.has_flag(Room.ROOM_DARK):

            def has_lit_light_source(objs):
                for obj in objs:
                    attrs = getattr(obj, "attributes", {})
                    # Any object with lit or turned_on and light/tool/lantern/torch/whatever
                    if (attrs.get("lit", False) or attrs.get("turned_on", False)) and (
                        attrs.get("light", False)
                        or obj.name.lower() in ["lantern", "lamp", "torch"]
                    ):
                        return True
                    # Check open containers recursively
                    if attrs.get("container", False) and attrs.get("open", False):
                        if has_lit_light_source(attrs.get("contents", [])):
                            return True
                return False

            # Check inventory and open containers for any lit/turned_on light source
            if has_lit_light_source(self.inventory):
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
                self.game_over()
        else:
            self.dark_moves = 0  # Reset counter if not in darkness

    def __init__(self, demo_mode=False, start_room=None):
        self.puzzles = {}  # Track puzzle states by room or puzzle name (must be first)
        self.BIGFIX = BIGFIX
        self.LOAD_MAX = LOAD_MAX
        import random

        self.dark_moves = 0  # Track moves/actions in darkness
        self.mailbox_open = False
        self.leaflet_taken = False
        self.lantern_lit = False
        self.rooms = load_rooms()
        print(f"[DEBUG] Loaded rooms: {list(self.rooms.keys())}")
        self.current_room = self._get_start_room()  # Fallback to default room
        # Allow case-insensitive and partial matching for start_room
        if start_room:
            # Try exact match first
            if start_room in self.rooms:
                self.current_room = start_room
            else:
                # Try case-insensitive match
                matches = [
                    rid for rid in self.rooms if rid.lower() == start_room.lower()
                ]
                if matches:
                    self.current_room = matches[0]
                else:
                    # Try partial match (case-insensitive)
                    partials = [
                        rid for rid in self.rooms if start_room.lower() in rid.lower()
                    ]
                    if partials:
                        self.current_room = partials[0]
        self.inventory = []
        self.score = 0
        self.flags = {}  # e.g., dark, dangerous, locked, etc.
        self.demo_mode = demo_mode
        self.thief_room = (
            self.current_room if self.demo_mode else None
        )  # Track Thief's current room
        self.thief_visible = False  # Is Thief currently visible to player?
        self.thief_cooldown = 0  # Moves until next possible encounter
        self.deaths = 0  # Track number of player deaths
        self.endgame = False  # Set to True if in endgame (expand as needed)
        from entities import Player

        start_room_id = (
            self.current_room
            if isinstance(self.current_room, str) and self.current_room
            else "WHOUS"
        )
        self.player = Player("Adventurer", start_room_id)
        if self.demo_mode:
            # Add all canonical NPCs to the actual starting room in demo mode
            demo_room = self.rooms.get(self.current_room)
            if demo_room:
                if not hasattr(demo_room, "npcs") or demo_room.npcs is None:
                    demo_room.npcs = []
                for npc in [THIEF, TROLL, CYCLOPS, GRUE, ROBOT]:
                    if npc not in demo_room.npcs:
                        demo_room.npcs.append(npc)
                # Give player all non-container objects from starting room, ignore carry limit
                if demo_room.objects:
                    non_containers = [
                        o
                        for o in demo_room.objects
                        if not o.attributes.get("container")
                    ]
                    self.inventory.extend(non_containers)
                    demo_room.objects = [
                        o for o in demo_room.objects if o.attributes.get("container")
                    ]
        if self.demo_mode:
            print(
                f"[Demo Mode] All non-container objects have been added to your inventory. Carry limits are disabled. Starting room: {self.current_room}"
            )

    def tick_thief(self):
        import random

        # Only run if Thief is enabled (demo or canonical rooms)
        if self.thief_room is None:
            return
        # Thief moves randomly between rooms
        room_ids = list(self.rooms.keys())
        # Thief should not move to rooms with 'dark' or 'locked' flags
        # Support both bitmask (int) and string-based flags
        from entities import Room as RoomFlags

        valid_rooms = []
        for rid in room_ids:
            flags = getattr(self.rooms[rid], "flags", [])
            # If flags is an int, treat as bitmask
            if isinstance(flags, int):
                is_dark = bool(flags & getattr(RoomFlags, "ROOM_DARK", 0))
                is_locked = bool(flags & getattr(RoomFlags, "ROOM_LOCKED", 0))
            else:
                # Otherwise, treat as iterable of strings
                if not isinstance(flags, (list, set, tuple)):
                    flags = [flags] if flags is not None else []
                is_dark = "dark" in flags
                is_locked = "locked" in flags
            if not is_dark and not is_locked:
                valid_rooms.append(rid)
        if not valid_rooms:
            valid_rooms = room_ids
        # Move thief every tick
        self.thief_room = random.choice(valid_rooms)

    def game_over(self, desc=None):
        room = self.rooms.get(self.current_room)
        # Prevent death in safe rooms
        if room and hasattr(room, "has_flag") and room.has_flag(Room.ROOM_SAFE):
            print("You feel completely safe here. Nothing can harm you.")
            return
        import sys

        # Canonical Zork death messages
        DEATH_MSG = desc or "You have died."
        SUICIDAL_MSG = (
            "Your adventure is over. You have died too many times.\n"
            "May your next life be more successful!"
        )
        ENDGAME_MSG = (
            "Normally I could attempt to rectify your condition, but I'm ashamed\n"
            "to say my abilities are not equal to dealing with your present state\n"
            "of disrepair. Permit me to express my profoundest regrets."
        )
        # Deduct points for dying
        self.score = max(0, self.score - 10)
        self.deaths += 1
        # Endgame death: immediate game over
        if getattr(self, "endgame", False):
            print(f"\n{ENDGAME_MSG}")
            self._final_quit(sys)
            return
        # Third death: game over
        if self.deaths >= 3:
            print(f"\n{SUICIDAL_MSG}")
            self._final_quit(sys)
            return
        # Standard death: respawn
        print(f"\n{DEATH_MSG}\nYou feel strangely disoriented, but alive.\n")
        self._respawn_player()
        if not sys.stdin.isatty():
            print("[Automated test mode: skipping restart/quit prompt]")
            return
        while True:
            choice = (
                input(
                    "Type 'restart' to play again, 'quit' to exit, or press Enter to continue: "
                )
                .strip()
                .lower()
            )
            if choice == "restart":
                print("Restarting game...\n")
                self.__init__(self.demo_mode)
                self.describe_current_room()
                break
            elif choice == "quit":
                print("Thanks for playing!")
                exit()
            elif choice == "":
                self.describe_current_room()
                break
            else:
                print("Please type 'restart', 'quit', or press Enter.")

    def _respawn_player(self):
        # Move player to starting room, reset health, clear inventory (canonical Zork drops inventory)
        self.current_room = self._get_start_room()
        self.player.health = self.player.max_health
        self.player.staggered = False
        # Drop all inventory in current room
        if self.inventory:
            room = self.rooms.get(self.current_room)
            if room:
                room.objects.extend(self.inventory)
        self.inventory = []

    def _final_quit(self, sys):
        print("\nGame over. Thanks for playing!")
        if not sys.stdin.isatty():
            return
        input("Press Enter to exit.")
        exit()
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
        room = self.rooms.get(self.current_room)
        if room and hasattr(room, "has_flag") and room.has_flag(Room.ROOM_NO_SAVE):
            print("You cannot save your game in this room.")
            return
        import random

        state = {
            "version": 1,
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
            "deaths": self.deaths,
            "endgame": self.endgame,
            "dark_moves": self.dark_moves,
            "demo_mode": self.demo_mode,
            "random_state": random.getstate(),
        }
        try:
            with open(filename, "wb") as f:
                pickle.dump(state, f)
            print(f"Game saved to {filename}.")
        except Exception as e:
            print(f"Error saving game: {e}")

    def load_game(self, filename="savegame.pkl"):
        room = self.rooms.get(self.current_room)
        if room and hasattr(room, "has_flag") and room.has_flag(Room.ROOM_NO_RESTORE):
            print("You cannot restore your game in this room.")
            return
        import random

        try:
            with open(filename, "rb") as f:
                state = pickle.load(f)
            # Versioning for future compatibility
            version = state.get("version", 1)
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
            self.deaths = state.get("deaths", self.deaths)
            self.endgame = state.get("endgame", self.endgame)
            self.dark_moves = state.get("dark_moves", self.dark_moves)
            self.demo_mode = state.get("demo_mode", self.demo_mode)
            if "random_state" in state:
                random.setstate(state["random_state"])
            print(f"Game loaded from {filename}.")
            self.describe_current_room()
        except Exception as e:
            print(f"Error loading game: {e}")

    def check_room_flags(self):
        room = self.rooms.get(self.current_room)
        if not room:
            return
        # Example: handle dark rooms
        if room.has_flag(Room.ROOM_DARK):
            print("It is pitch dark. You are likely to be eaten by a grue.")
        # Example: handle locked rooms
        # if room.has_flag(Room.ROOM_LOCKED):
        #     print("The room is locked.")
        # Add more flag logic as needed
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
        if room and not getattr(room, "visited", False):
            room.visited = True
            # Optionally award points for first visit
            # self.score += 1
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
        # Water/air room logic
        if room:
            if hasattr(room, "has_flag") and room.has_flag(Room.ROOM_WATER):
                has_boat = any(
                    obj.name.lower() in ["boat", "raft"] for obj in self.inventory
                )
                if not has_boat:
                    print("You need a boat to travel here, or you will drown!")
                    self.game_over("You have drowned.")
                    return
            if hasattr(room, "has_flag") and room.has_flag(Room.ROOM_AIR):
                has_mask = any(
                    obj.name.lower() in ["mask", "air supply"] for obj in self.inventory
                )
                if not has_mask:
                    print("You cannot breathe here without an air supply!")
                    self.game_over("You have suffocated.")
                    return
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
            print("You are carrying:")
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
            print("You are empty-handed.")


if __name__ == "__main__":
    import sys

    demo_mode = False
    start_room = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            demo_mode = True
            if len(sys.argv) > 2:
                start_room = sys.argv[2]
        else:
            start_room = sys.argv[1]
    print(
        "Welcome to Phork! Type 'look' to see your surroundings, 'go <direction>' to move, 'inventory' to check your items, or 'quit' to exit."
    )
    if demo_mode:
        print(
            f"[Demo Mode Enabled] Carry limits are disabled and all starting objects are in your inventory. Starting room: {start_room if start_room else 'default'}"
        )
    game = Game(demo_mode=demo_mode, start_room=start_room)
    game.describe_current_room()
    while True:
        command = input("\n> ")
        from command_parser import parse_command

        if not parse_command(game, command):
            break
