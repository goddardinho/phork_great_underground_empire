from typing import Any, Optional


# Canonical NPC base class
class NPC:
    def __init__(
        self,
        name: str,
        description: str,
        state: Optional[dict] = None,
        max_health: int = 1,
    ):
        self.name = name
        self.description = description
        self.state = state if state is not None else {}
        self.alive = True
        self.max_health = max_health
        self.health = max_health
        self.wounds = 0
        self.staggered = False

    def is_dead(self):
        return not self.alive or self.health <= 0

    def is_staggered(self):
        return self.staggered

    def interact(self, game, action: Optional[str] = None, item: Any = None) -> str:
        return f"You interact with {self.name}."


# Canonical NPCs
class Thief(NPC):
    def __init__(self):
        # Canonical Zork: Thief is tough, takes several hits
        super().__init__(
            "Thief",
            "A sneaky thief lurks here, eyeing your valuables. He wields a razor-sharp stiletto and moves with uncanny stealth.",
            max_health=3,
        )
        self.weapon = "stiletto"
        self.attack_method = "strikes swiftly with his stiletto"

    def interact(self, game, action: Optional[str] = None, item: Any = None) -> str:
        if not self.alive:
            return "The thief is dead."
        if action in ("talk", "greet", "hello"):
            return "The thief ignores you."
        elif action in ("fight", "attack", "kill", "stab", "hit"):
            import random

            # 70% chance to wound, 20% miss, 10% critical (kill)
            roll = random.random()
            if roll < 0.1:
                self.health = 0
            elif roll < 0.8:
                self.health -= 1
            # else: miss
            if self.health <= 0:
                self.alive = False
                room = game.rooms.get(game.current_room)
                if room and hasattr(room, "npcs") and self in room.npcs:
                    room.npcs.remove(self)
                return "You finally defeat the thief! He collapses and vanishes, leaving his treasures behind."
            elif roll < 0.8:
                return (
                    "You wound the thief! He snarls and fights back. (Health: %d)"
                    % self.health
                )
            else:
                return "You miss! The thief dodges and grins."
        elif action in ("give", "bribe"):
            if item and item.name.lower() in (
                "jewel",
                "diamond",
                "coin",
                "gold",
                "treasure",
            ):
                return "The thief snatches the treasure, bows mockingly, and vanishes into the shadows!"
            elif item:
                return f'The thief glances at the {item.name} and sneers, "Not interested."'
            else:
                return "The thief looks at your empty hands and laughs."
        elif action in ("take", "grab"):
            return "The thief slips from your grasp with practiced ease."
        elif action in ("tie",):
            return "You cannot tie the thief; he is far too quick."
        elif action in ("poke",):
            return 'The thief says, "Hands off!" and steps away.'
        else:
            return "The thief eyes you suspiciously."


class Troll(NPC):
    def __init__(self):
        # Canonical Zork: Troll is tough, takes several hits
        super().__init__(
            "Troll",
            "A menacing troll blocks the bridge, demanding payment. He wields a bloody axe and swings it with brutal force.",
            max_health=2,
        )
        self.weapon = "bloody axe"
        self.attack_method = "swings his bloody axe at you"

    def interact(self, game, action: Optional[str] = None, item: Any = None) -> str:
        if not self.alive:
            return "The troll is dead."
        if action in ("talk", "greet", "hello"):
            return 'The troll grunts, "No talk. Pay toll!"'
        elif action in ("fight", "attack", "kill", "stab", "hit"):
            import random

            roll = random.random()
            if roll < 0.15:
                self.health = 0
            elif roll < 0.85:
                self.health -= 1
            # else: miss
            if self.health <= 0:
                self.alive = False
                room = game.rooms.get(game.current_room)
                if room and hasattr(room, "npcs") and self in room.npcs:
                    room.npcs.remove(self)
                return "You defeat the troll! He falls to the ground and disappears."
            elif roll < 0.85:
                return (
                    "You wound the troll! He roars in pain. (Health: %d)" % self.health
                )
            else:
                return "You miss! The troll swings his club at you."
        elif action in ("give", "bribe"):
            if item and item.name.lower() in ("coin", "gold", "treasure"):
                return "The troll snatches the treasure, grins, and steps aside."
            elif item:
                return f"The troll sniffs the {item.name} and tosses it aside."
            else:
                return "The troll looks at your empty hands and growls."
        elif action in ("take", "grab"):
            return "The troll is much too strong for you to grab."
        elif action in ("tie",):
            return "You cannot tie the troll; he is far too strong."
        elif action in ("poke",):
            return 'The troll roars, "No poke!" and swings his club.'
        else:
            return "The troll grunts and blocks your way."


class Cyclops(NPC):
    def __init__(self):
        # Canonical Zork: Cyclops is very tough
        super().__init__(
            "Cyclops",
            "A huge cyclops glares at you, hungry and irritable. He attacks with his massive fists and throws objects with terrifying strength.",
            max_health=4,
        )
        self.weapon = "fists"
        self.attack_method = "smashes at you with his fists or hurls objects"

    def interact(self, game, action: Optional[str] = None, item: Any = None) -> str:
        if not self.alive:
            return "The cyclops is dead."
        if action in ("talk", "greet", "hello"):
            return "The cyclops ignores your words and glares hungrily."
        elif action in ("fight", "attack", "kill", "stab", "hit"):
            import random

            roll = random.random()
            if roll < 0.08:
                self.health = 0
            elif roll < 0.88:
                self.health -= 1
            # else: miss
            if self.health <= 0:
                self.alive = False
                room = game.rooms.get(game.current_room)
                if room and hasattr(room, "npcs") and self in room.npcs:
                    room.npcs.remove(self)
                return "You slay the cyclops! He crashes to the ground and is no more."
            elif roll < 0.88:
                return (
                    "You wound the cyclops! He bellows in rage. (Health: %d)"
                    % self.health
                )
            else:
                return "You miss! The cyclops shrugs off your attack."
        elif action in ("give", "bribe"):
            if item and item.name.lower() in (
                "food",
                "meat",
                "sandwich",
                "lunch",
                "garlic",
            ):
                return "The cyclops may be hungry, but there is a limit."
            elif item:
                return f"The cyclops is not so stupid as to eat {item.name}!"
            else:
                return "The cyclops looks at your empty hands and snorts."
        elif action in ("take", "grab"):
            return "The cyclops doesn't take kindly to being grabbed."
        elif action in ("tie",):
            return "You cannot tie the cyclops, though he is fit to be tied."
        elif action in ("poke",):
            return "'Do you think I'm as stupid as my father was?', he says, dodging."
        else:
            return "The cyclops snorts and looks hungry."


class Grue(NPC):
    def __init__(self):
        super().__init__(
            "Grue", "It is pitch dark. You are likely to be eaten by a grue."
        )

    def interact(self, game, action: Optional[str] = None, item: Any = None) -> str:
        if action in ("talk", "greet", "hello"):
            return "It is pitch black. You are likely to be eaten by a grue!"
        elif action in ("fight", "attack", "kill", "stab", "hit"):
            return "You swing wildly in the dark. Something growls."
        elif action in ("give", "bribe"):
            return "You can't see the grue, let alone give it anything."
        elif action in ("take", "grab"):
            return "You can't grab what you can't see."
        elif action in ("tie",):
            return "You can't tie what you can't see."
        elif action in ("poke",):
            return "You poke into the darkness. Something pokes back!"
        else:
            return "You cannot see the grue, but you feel its presence."


class Robot(NPC):
    def __init__(self):
        super().__init__("Robot", "A silent robot stands here.")

    def interact(self, game, action: Optional[str] = None, item: Any = None) -> str:
        if action in ("talk", "greet", "hello"):
            return 'The robot beeps: "Awaiting command."'
        elif action in ("fight", "attack", "kill", "stab", "hit"):
            return "The robot's metal shell is undamaged by your attack."
        elif action in ("give", "bribe"):
            if item:
                return (
                    f"The robot accepts the {item.name} and stores it in a compartment."
                )
            else:
                return "The robot awaits an object."
        elif action in ("take", "grab"):
            return "The robot is too heavy to move."
        elif action in ("tie",):
            return "You cannot tie the robot."
        elif action in ("poke",):
            return "The robot emits a soft beep."
        else:
            return "The robot stands silently, awaiting orders."


# NPC singletons for use in rooms
THIEF = Thief()
TROLL = Troll()
CYCLOPS = Cyclops()
GRUE = Grue()
ROBOT = Robot()

from typing import Optional, List, Dict
from objects import GameObject


class Room:
    # Room flag bitfield constants
    ROOM_DARK = 0x01
    ROOM_VISITED = 0x02
    ROOM_DEADLY = 0x04
    # Add more as needed

    def __init__(
        self,
        id: str,
        desc_long: str,
        desc_short: str,
        exits: Dict[str, str],
        objects: List[GameObject],
        flags: int = 0,
        action: Optional[str] = None,
        locked_exits: Optional[Dict[str, bool]] = None,
        npcs: Optional[list] = None,
    ):
        self.id = id
        self.desc_long = desc_long
        self.desc_short = desc_short
        self.exits = exits
        self.objects = objects
        self.flags = flags
        self.action = action
        self.locked_exits = locked_exits if locked_exits is not None else {}
        self.npcs = npcs if npcs is not None else []

    def set_flag(self, flag: int):
        self.flags |= flag

    def clear_flag(self, flag: int):
        self.flags &= ~flag

    def has_flag(self, flag: int) -> bool:
        return (self.flags & flag) != 0


class Player:
    def __init__(self, name: str, current_room: str):
        self.name = name
        self.current_room = current_room
        self.inventory: List[GameObject] = []
        self.max_health = 3
        self.health = 3
        self.wounds = 0
        self.staggered = False

    def is_dead(self):
        return self.health <= 0

    def is_staggered(self):
        return self.staggered



class Action:
    def __init__(self, name: str, function):
        self.name = name
        self.function = function  # Callable for action logic


class NPC:
    def __init__(
        self,
        name: str,
        description: str,
        location: Optional[str] = None,
        hostile: bool = False,
        inventory: Optional[List[GameObject]] = None,
    ):
        self.name = name
        self.description = description
        self.location = location  # Room id or None
        self.hostile = hostile
        self.inventory = inventory if inventory is not None else []
        self.state: Dict[str, any] = {}

    def interact(
        self, player, action: Optional[str] = None, item: Optional[GameObject] = None
    ):
        # Canonical Zork I NPC logic
        if self.name == "Troll":
            if action == "fight":
                print(
                    "You fight the troll! If you win, he cowers and pleads for his life."
                )
                self.state["disarmed"] = True
                self.hostile = False
                return True
            elif action == "give" and item:
                if item.name.lower() == "knife":
                    print(
                        "The troll, sated, throws the knife back. He does not look pleased."
                    )
                    return True
                else:
                    print(f"The troll graciously accepts the {item.name}.")
                    self.inventory.append(item)
                    return True
            elif action == "bribe" and item:
                print(f"The troll accepts your bribe: {item.name}.")
                self.inventory.append(item)
                self.hostile = False
                return True
            elif action == "hello":
                print("Unfortunately, the troll can't hear you.")
                return False
            print("The troll blocks your way, demanding payment or a fight.")
            return False
        elif self.name == "Cyclops":
            if action == "give" and item:
                if item.name.lower() == "food":
                    print("The cyclops eats the food and calms down.")
                    self.state["wrath"] = max(self.state.get("wrath", 0) - 1, -1)
                    return True
                elif item.name.lower() == "water":
                    print("The cyclops drinks and falls asleep.")
                    self.state["asleep"] = True
                    self.hostile = False
                    return True
                else:
                    print(f"The cyclops refuses your {item.name}.")
                    return False
                # Canonical: Cyclops flees if given 'Odysseus' keyword
                if item.name.lower() == "odysseus":
                    print(
                        "The cyclops, hearing the name of his father's deadly nemesis, flees the room in terror!"
                    )
                    self.state["odysseus"] = True
                    self.hostile = False
                    return True
            elif action == "attack":
                print("The cyclops shrugs off your attack.")
                self.state["wrath"] = self.state.get("wrath", 0) + 1
                return False
            elif action == "wake":
                print("The cyclops yawns and stares at you.")
                self.state["asleep"] = False
                self.hostile = True
                return True
            print("The cyclops glares at you, hungry and irritable.")
            return False
        elif self.name == "Thief":
            if action == "fight":
                print("You fight the thief! If you win, he drops his loot and flees.")
                self.state["defeated"] = True
                self.inventory.clear()
                return True
            elif action == "give" and item:
                print(
                    f"The thief accepts your {item.name}, but may steal from you later."
                )
                self.inventory.append(item)
                return True
            elif action == "steal":
                print("The thief attempts to steal your valuables.")
                # Example: remove a random item from player inventory
                if player.inventory:
                    stolen = player.inventory.pop()
                    self.inventory.append(stolen)
                    print(f"The thief stole your {stolen.name}!")
                    return True
                print("The thief finds nothing to steal.")
                return False
            print("The thief lurks in the shadows, watching you.")
            return False
        print(f"{self.name} does not respond.")
        return False


# Example NPCs (expanded for canonical logic)
THIEF = NPC("Thief", "A sneaky thief lurks here, eyeing your valuables.", hostile=True)
TROLL = NPC(
    "Troll", "A menacing troll blocks the bridge, demanding payment.", hostile=True
)
CYCLOPS = NPC(
    "Cyclops", "A huge cyclops glares at you, hungry and irritable.", hostile=True
)


# Grue: special event NPC, not visible, eats player in dark rooms
class Grue(NPC):
    def __init__(self):
        super().__init__(
            "Grue",
            "It is pitch black. You are likely to be eaten by a grue.",
            hostile=True,
        )

    def interact(self, player, action=None, item=None):
        return "Oh, no! You walked into the slavering fangs of a lurking grue."


GRUE = Grue()


# Robot: commandable NPC in Maintenance Room
class Robot(NPC):
    def __init__(self):
        super().__init__(
            "Robot",
            "A shiny, silent robot stands here, awaiting orders.",
            hostile=False,
        )
        self.activated = False

    def interact(self, player, action=None, item=None):
        if action == "activate":
            if not self.activated:
                self.activated = True
                return "The robot whirs to life and awaits your command."
            else:
                return "The robot is already active."
        elif action == "command":
            if self.activated:
                return "The robot obeys your command."
            else:
                return "The robot does not respond. It must be activated first."
        else:
            return "The robot stands silently."


ROBOT = Robot()
