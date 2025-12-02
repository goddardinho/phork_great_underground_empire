from typing import Optional, List, Dict
from objects import GameObject


class Room:
    def __init__(
        self,
        id: str,
        desc_long: str,
        desc_short: str,
        exits: Dict[str, str],
        objects: List[GameObject],
        flags: List[str] = [],
        action: Optional[str] = None,
        locked_exits: Optional[Dict[str, bool]] = None,
        npcs: Optional[List["NPC"]] = None,
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


class Player:
    def __init__(self, name: str, current_room: str):
        self.name = name
        self.current_room = current_room
        self.inventory: List[GameObject] = []


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
