from typing import Any

# Canonical NPC base class
class NPC:
    def __init__(self, name: str, description: str, state: Optional[dict] = None):
        self.name = name
        self.description = description
        self.state = state if state is not None else {}
    def interact(self, game, action: str = None, item: Any = None) -> str:
        return f"You interact with {self.name}."

# Canonical NPCs
class Thief(NPC):
    def __init__(self):
        super().__init__("Thief", "A sneaky thief lurks here, eyeing your valuables.")
    def interact(self, game, action: str = None, item: Any = None) -> str:
        if action in ("talk", "greet", "hello"):
            return "The thief ignores you."
        elif action in ("fight", "attack", "kill", "stab", "hit"):
            return "The thief deftly dodges your attack and grins."
        elif action in ("give", "bribe"):
            if item and item.name.lower() in ("jewel", "diamond", "coin", "gold", "treasure"):
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
        super().__init__("Troll", "A menacing troll blocks the bridge, demanding payment.")
    def interact(self, game, action: str = None, item: Any = None) -> str:
        if action in ("talk", "greet", "hello"):
            return 'The troll grunts, "No talk. Pay toll!"'
        elif action in ("fight", "attack", "kill", "stab", "hit"):
            return "The troll swings his club at you! You barely dodge."
        elif action in ("give", "bribe"):
            if item and item.name.lower() in ("coin", "gold", "treasure"):
                return "The troll snatches the treasure, grins, and steps aside."
            elif item:
                return f'The troll sniffs the {item.name} and tosses it aside.'
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
        super().__init__("Cyclops", "A huge cyclops glares at you, hungry and irritable.")
    def interact(self, game, action: str = None, item: Any = None) -> str:
        if action in ("talk", "greet", "hello"):
            return 'The cyclops ignores your words and glares hungrily.'
        elif action in ("fight", "attack", "kill", "stab", "hit"):
            return "The cyclops ignores all injury to his body with a shrug."
        elif action in ("give", "bribe"):
            if item and item.name.lower() in ("food", "meat", "sandwich", "lunch", "garlic"):
                return "The cyclops may be hungry, but there is a limit."
            elif item:
                return f'The cyclops is not so stupid as to eat {item.name}!'
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
        super().__init__("Grue", "It is pitch dark. You are likely to be eaten by a grue.")
    def interact(self, game, action: str = None, item: Any = None) -> str:
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
    def interact(self, game, action: str = None, item: Any = None) -> str:
        if action in ("talk", "greet", "hello"):
            return 'The robot beeps: "Awaiting command."'
        elif action in ("fight", "attack", "kill", "stab", "hit"):
            return "The robot's metal shell is undamaged by your attack."
        elif action in ("give", "bribe"):
            if item:
                return f'The robot accepts the {item.name} and stores it in a compartment.'
            else:
                return "The robot awaits an object."
        elif action in ("take", "grab"):
            return "The robot is too heavy to move."
        elif action in ("tie",):
            return "You cannot tie the robot."
        elif action in ("poke",):
            return 'The robot emits a soft beep.'
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
    def __init__(self, id: str, desc_long: str, desc_short: str, exits: Dict[str, str], objects: List[GameObject], flags: List[str] = [], action: Optional[str] = None, locked_exits: Optional[Dict[str, bool]] = None, npcs: Optional[list] = None):
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
