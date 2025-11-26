# Multi-step Troll Bridge Puzzle
def troll_bridge_puzzle(game, action=None):
    state = game.puzzles.setdefault("troll_bridge_puzzle", {"stage": 1, "crossed": False})
    if action == "pay" and state["stage"] == 1:
        print("You hand the troll a coin. He steps aside and lets you cross the bridge.")
        state["stage"] = 2
        return True
    elif action == "cross" and state["stage"] == 2:
        print("You cross the bridge.")
        state["crossed"] = True
        game.score += 5
        return True
    elif state["crossed"]:
        print("You have already crossed the bridge.")
        return False
    print("Nothing happens.")
    return False

# Multi-step Cyclops Puzzle
def cyclops_puzzle(game, action=None):
    state = game.puzzles.setdefault("cyclops_puzzle", {"stage": 1, "asleep": False})
    if action == "feed" and state["stage"] == 1:
        print("You give the cyclops food. He eats and falls asleep, snoring loudly.")
        state["stage"] = 2
        state["asleep"] = True
        game.score += 7
        return True
    elif state["asleep"]:
        print("The cyclops is already asleep.")
        return False
    print("Nothing happens.")
    return False

# Multi-step Trap Door Puzzle
def trap_door_puzzle(game, action=None):
    state = game.puzzles.setdefault("trap_door_puzzle", {"stage": 1, "unlocked": False})
    if action == "unlock" and state["stage"] == 1:
        print("You unlock the trap door. It creaks open, revealing a dark staircase.")
        state["stage"] = 2
        state["unlocked"] = True
        game.score += 4
        return True
    elif state["unlocked"]:
        print("The trap door is already unlocked.")
        return False
    print("Nothing happens.")
    return False

# Multi-step Volcano Puzzle
def volcano_puzzle(game, action=None):
    state = game.puzzles.setdefault("volcano_puzzle", {"stage": 1, "erupted": False})
    if action == "throw" and state["stage"] == 1:
        print("You throw the item into the volcano. The ground shakes and smoke billows out!")
        state["stage"] = 2
        state["erupted"] = True
        game.score += 11
        return True
    elif state["erupted"]:
        print("The volcano has already erupted.")
        return False
    print("Nothing happens.")
    return False

# Multi-step Ladder Puzzle
def ladder_puzzle(game, action=None):
    state = game.puzzles.setdefault("ladder_puzzle", {"stage": 1, "escaped": False})
    if action == "use" and state["stage"] == 1:
        print("With the help of the ladder, you exit the puzzle room!")
        state["stage"] = 2
        state["escaped"] = True
        game.score += 4
        return True
    elif state["escaped"]:
        print("You have already escaped using the ladder.")
        return False
    print("Nothing happens.")
    return False

# Multi-step Museum Pass Puzzle
def museum_pass_puzzle(game, action=None):
    state = game.puzzles.setdefault("museum_pass_puzzle", {"stage": 1, "entered": False})
    if action == "show" and state["stage"] == 1:
        print("The guard inspects your pass and lets you in.")
        state["stage"] = 2
        state["entered"] = True
        game.score += 2
        return True
    elif state["entered"]:
        print("You have already entered the museum.")
        return False
    print("Nothing happens.")
    return False

# Multi-step Trophy Case Puzzle
def trophy_case_puzzle(game, action=None):
    state = game.puzzles.setdefault("trophy_case_puzzle", {"stage": 1, "placed": False})
    if action == "place" and state["stage"] == 1:
        print("You place the treasure in the trophy case. Well done!")
        state["stage"] = 2
        state["placed"] = True
        game.score += 10
        return True
    elif state["placed"]:
        print("The trophy case already contains the treasure.")
        return False
    print("Nothing happens.")
    return False

# Multi-step Grue Danger Puzzle
def grue_puzzle(game, action=None):
    state = game.puzzles.setdefault("grue_puzzle", {"stage": 1, "danger": False})
    if action == "enter" and state["stage"] == 1:
        print("It is pitch dark. You are likely to be eaten by a grue!")
        state["stage"] = 2
        state["danger"] = True
        game.score -= 5
        return True
    elif state["danger"]:
        print("You are already in danger from the grue.")
        return False
    print("Nothing happens.")
    return False

# Multi-step Villain Puzzle
def villain_puzzle(game, action=None):
    state = game.puzzles.setdefault("villain_puzzle", {"stage": 1, "defeated": False})
    if action == "fight" and state["stage"] == 1:
        print("You fight the villain!")
        state["stage"] = 2
        return True
    elif action == "defeat" and state["stage"] == 2:
        print("You have defeated the villain!")
        state["defeated"] = True
        game.score += 10
        return True
    elif state["defeated"]:
        print("You have already defeated the villain!")
        return False
    print("Nothing happens.")
    return False

# Button puzzle (Secret Room)
def button_puzzle(game):
    if not game.puzzles.get("button_puzzle"):
        print("Click! A section of the wall slides open, revealing a secret passage.")
        game.score += 7
        game.puzzles["button_puzzle"] = True
        return True
    print("Nothing happens.")
    return False

# Dial puzzle (Machine Room)
def dial_puzzle(game):
    if not game.puzzles.get("dial_puzzle"):
        print("The dial turns with a satisfying click. The machine whirs and starts up.")
        game.score += 5
        game.puzzles["dial_puzzle"] = True
        return True
    print("The dial won't budge any further.")
    return False

def thief_puzzle(game, action=None):
    state = game.puzzles.setdefault("thief_puzzle", {"stage": 1, "treasure_recovered": False})
    if action == "track" and state["stage"] == 1:
        print("You track the thief to his lair.")
        state["stage"] = 2
        return True
    elif action == "fight" and state["stage"] == 2:
        print("You fight the thief and recover your treasure!")
    state = game.puzzles.setdefault("rainbow_puzzle", {"stage": 1, "solid": False})
    if action == "solidify" and state["stage"] == 1:
        print("The rainbow shimmers and becomes solid. You can cross to the other side!")
        state["stage"] = 2
        state["solid"] = True
        game.score += 4
        return True
    elif state["solid"]:
        print("The rainbow is already solid.")
        return False
# Add more puzzle handlers as needed, matching source logic


def unlock_door_puzzle(game, direction):
    """Triggered by unlocking a special door."""
    key = "unlock_door_" + direction
    if not game.puzzles.get(key):
        print(f"You unlock the {direction} door. It swings open quietly.")
        game.score += 2  # Example value, update from source
        game.puzzles[key] = True
        return True
    print(f"The {direction} door is already unlocked.")
    return False




# Puzzle handler functions (examples, expand as needed)


# Egg puzzle (for combining egg and canary)
def egg_puzzle(game, action=None):
    if action == "open" and not game.puzzles.get("egg_puzzle"):
        print("You open the jewel-encrusted egg. Inside is a golden canary! Score!")
        game.score += 5  # Source: OTVAL for egg/canary
        game.puzzles["egg_puzzle"] = True
        return True
    print("The egg is already open.")
    return False


# Flood control dam puzzle
def dam_puzzle(game, action=None):
    if action == "open" and not game.puzzles.get("dam_puzzle"):
        print("You open the flood control dam #3. Water rushes through the sluice gate!")
        game.score += 10  # Source: dam puzzle value
        game.puzzles["dam_puzzle"] = True
        return True
    print("The dam is already open.")
    return False


# Rainbow bridge puzzle
def rainbow_puzzle(game, action=None):
    if action == "solidify" and not game.puzzles.get("rainbow_puzzle"):
        print("The rainbow shimmers and becomes solid. You can cross to the other side!")
        game.score += 4  # Source: rainbow puzzle value
        game.puzzles["rainbow_puzzle"] = True
        return True
    print("The rainbow is already solid.")
    return False


# Villain defeat puzzle example
# def villain_puzzle(game, action=None):
#     state = game.puzzles.setdefault("villain_puzzle", {"stage": 1, "defeated": False})
#     if action == "fight" and state["stage"] == 1:
#         print("You fight the villain!")
#         state["stage"] = 2
#         return True
#     elif action == "defeat" and state["stage"] == 2:
#         print("You have defeated the villain!")
#         state["defeated"] = True
#         game.score += 10
#         return True
#     elif state["defeated"]:
#         print("You have already defeated the villain!")
#         return False
#     print("Nothing happens.")
#     return False


# Generic puzzle handler
def generic_puzzle(game):
    if not game.puzzles.get("generic_puzzle"):
        print("You solved the puzzle!")
        game.score += 5  # Example value, update from source
        game.puzzles["generic_puzzle"] = True
        return True
    return False


# Riddle puzzle handler
def riddle_puzzle(game):
    if not game.puzzles.get("riddle_puzzle"):
        print("You answered the riddle correctly!")
        game.score += 6  # Example value, update from source
        game.puzzles["riddle_puzzle"] = True
        return True
    return False


# Mailbox puzzle handler
def mailbox_puzzle(game):
    if not game.puzzles.get("mailbox_puzzle"):
        print("You open the mailbox. Inside is a leaflet!")
        game.score += 1
        game.puzzles["mailbox_puzzle"] = True
        return True
    print("The mailbox is already open.")
    return False


# Grue puzzle handler (enter dark room)
# def grue_puzzle(game, action=None):
#     if not game.puzzles.get("grue_puzzle"):
#         print("It is pitch dark. You are likely to be eaten by a grue!")
#         game.score -= 5
#         game.puzzles["grue_puzzle"] = True
#         return True
#     print("You are already in danger from the grue.")
#     return False


# Victory puzzle handler
def victory_puzzle(game):
    if not game.puzzles.get("victory_puzzle"):
        print("Congratulations! You have won the game!")
        game.score += 35
        game.puzzles["victory_puzzle"] = True
        return True
    print("You have already won.")
    return False


# Puzzle registry: maps triggers to handler functions
## Puzzle registry: maps triggers to handler functions

# Place this at the end of the file, after all handler definitions
PUZZLE_REGISTRY = {
    # Troll bridge puzzle (multi-step)
    ("troll", "pay"): lambda game, action=None: troll_bridge_puzzle(game, action),
    ("troll", "cross"): lambda game, action=None: troll_bridge_puzzle(game, action),
    # Cyclops puzzle (multi-step)
    ("cyclops", "feed"): lambda game, action=None: cyclops_puzzle(game, action),
    # Thief puzzle (multi-step)
    ("thief", "track"): lambda game, action=None: thief_puzzle(game, action),
    ("thief", "fight"): lambda game, action=None: thief_puzzle(game, action),
    # Trap door puzzle (multi-step)
    ("trap door", "unlock"): lambda game, action=None: trap_door_puzzle(game, action),
    # Volcano puzzle (multi-step)
    ("volcano", "throw"): lambda game, action=None: volcano_puzzle(game, action),
    # Egg/Canary puzzle (multi-step)
    ("egg", "open"): lambda game, action=None: egg_puzzle(game, action),
    # Dam puzzle (multi-step)
    ("dam", "open"): lambda game, action=None: dam_puzzle(game, action),
    # Rainbow bridge puzzle (multi-step)
    ("rainbow", "solidify"): lambda game, action=None: rainbow_puzzle(game, action),
    # Trophy case puzzle (multi-step)
    ("trophy case", "place"): lambda game, action=None: trophy_case_puzzle(game, action),
    # Grue danger puzzle (multi-step)
    ("grue", "enter"): lambda game, action=None: grue_puzzle(game, action),
    # Ladder puzzle (multi-step)
    ("ladder", "use"): lambda game, action=None: ladder_puzzle(game, action),
    # Museum pass puzzle (multi-step)
    ("museum", "show"): lambda game, action=None: museum_pass_puzzle(game, action),
    # Villain defeat puzzle (multi-step)
    ("villain", "fight"): lambda game, action=None: villain_puzzle(game, action),
    ("villain", "defeat"): lambda game, action=None: villain_puzzle(game, action),
    # Button puzzle (Secret Room)
    "push button": button_puzzle,
    "press button": button_puzzle,  # synonym
    # Dial puzzle (Machine Room)
    "turn dial": dial_puzzle,
    "rotate dial": dial_puzzle,  # synonym
    # Unlock door puzzles (example directions)
    ("unlock", "north"): lambda game: unlock_door_puzzle(game, "north"),
    ("unlock", "east"): lambda game: unlock_door_puzzle(game, "east"),
    ("unlock", "west"): lambda game: unlock_door_puzzle(game, "west"),
    ("unlock", "south"): lambda game: unlock_door_puzzle(game, "south"),
    # Ladder puzzle (Chinese Puzzle Room)
    "use ladder": ladder_puzzle,
    "climb ladder": ladder_puzzle,
    # Museum puzzle (Royal Zork Puzzle Museum)
    "show pass": museum_pass_puzzle,
    "use pass": museum_pass_puzzle,
    # Villain defeat puzzle (multi-step)
    "defeat villain": villain_puzzle,
    "kill villain": villain_puzzle,
    "fight villain": villain_puzzle,
    # Mailbox puzzle
    "open mailbox": mailbox_puzzle,
    # Grue puzzle (enter dark room)
    "enter dark room": lambda game: grue_puzzle(game, "enter"),
    # Victory puzzle
    "win game": victory_puzzle,
    # Multi-step puzzle triggers (examples)
    "solve puzzle": generic_puzzle,
    "complete puzzle": generic_puzzle,
    "answer riddle": riddle_puzzle,
    "say answer": riddle_puzzle,
    # Add more as needed from source
}

# Utility: trigger a puzzle by name or action


def trigger_puzzle(game, trigger, *args):
    """Call the appropriate puzzle handler from the registry."""
    handler = PUZZLE_REGISTRY.get(trigger)
    if not handler and isinstance(trigger, tuple):
        handler = PUZZLE_REGISTRY.get(tuple(trigger))
    if handler:
        return handler(game, *args)
    print("Nothing happens.")
    return False


# Example: import and use in main.py or parser
# from puzzles import trigger_puzzle
# trigger_puzzle(game, 'push button')
# trigger_puzzle(game, ('unlock', 'north'))
