# Mailbox/leaflet puzzle
def mailbox_puzzle(game):
    if not game.puzzles.get("mailbox_puzzle"):
        print("You open the small mailbox. Inside is a leaflet.")
        game.score += 1  # Source: mailbox puzzle value
        game.puzzles["mailbox_puzzle"] = True
        return True
    print("The mailbox is already open.")
    return False


# Lantern puzzle (turning on/off)
def lantern_puzzle(game):
    if not game.puzzles.get("lantern_puzzle"):
        print("The brass lantern is now on. The room is illuminated.")
        game.score += 2  # Source: lantern puzzle value
        game.puzzles["lantern_puzzle"] = True
        return True
    print("The lantern is already on.")
    return False


# Troll bridge puzzle
def troll_bridge_puzzle(game):
    if not game.puzzles.get("troll_bridge_puzzle"):
        print(
            "You hand the troll a coin. He steps aside and lets you cross the bridge."
        )
        game.score += 5  # Source: troll bridge value
        game.puzzles["troll_bridge_puzzle"] = True
        return True
    print("The troll has already let you pass.")
    return False


# Cyclops puzzle
def cyclops_puzzle(game):
    if not game.puzzles.get("cyclops_puzzle"):
        print("You give the cyclops food. He eats and falls asleep, snoring loudly.")
        game.score += 7  # Source: cyclops puzzle value
        game.puzzles["cyclops_puzzle"] = True
        return True
    print("The cyclops is already asleep.")
    return False


# Thief puzzle
def thief_puzzle(game):
    if not game.puzzles.get("thief_puzzle"):
        print("You outwit the thief and reclaim your stolen treasure!")
        game.score += 9  # Source: thief puzzle value
        game.puzzles["thief_puzzle"] = True
        return True
    print("The thief has already been defeated.")
    return False


# Trap door puzzle
def trap_door_puzzle(game):
    if not game.puzzles.get("trap_door_puzzle"):
        print("You unlock the trap door. It creaks open, revealing a dark staircase.")
        game.score += 4  # Source: trap door value
        game.puzzles["trap_door_puzzle"] = True
        return True
    print("The trap door is already unlocked.")
    return False


# Volcano puzzle
def volcano_puzzle(game):
    if not game.puzzles.get("volcano_puzzle"):
        print(
            "You throw the item into the volcano. The ground shakes and smoke billows out!"
        )
        game.score += 11  # Source: volcano puzzle value
        game.puzzles["volcano_puzzle"] = True
        return True
    print("The volcano has already erupted.")
    return False


# Endgame victory puzzle
def victory_puzzle(game):
    if not game.puzzles.get("victory_puzzle"):
        print(
            "*** Congratulations! You have solved all the puzzles and won the game! ***"
        )
        game.score += 35  # Source: endgame victory value
        game.puzzles["victory_puzzle"] = True
        return True
    print("You have already won the game.")
    return False


"""
puzzles.py - Puzzle logic, registry, and source mapping for Zork-like gameplay
"""


# Puzzle handler functions (examples, expand as needed)
def button_puzzle(game):
    """Triggered by PUSH BUTTON in Secret Room."""
    if not game.puzzles.get("button_puzzle"):
        print("Click! A section of the wall slides open, revealing a secret passage.")
        game.score += 7  # Source: WHOUS puzzle value
        game.puzzles["button_puzzle"] = True
        return True
    print("Nothing happens.")
    return False


def dial_puzzle(game):
    """Triggered by TURN DIAL in Machine Room."""
    if not game.puzzles.get("dial_puzzle"):
        print(
            "The dial turns with a satisfying click. The machine whirs and starts up."
        )
        game.score += 5  # Example value, update from source
        game.puzzles["dial_puzzle"] = True
        return True
    print("The dial won't budge any further.")
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

    # Ladder puzzle example
    def ladder_puzzle(game):
        if not game.puzzles.get("ladder_puzzle"):
            print("With the help of the ladder, you exit the puzzle room!")
            game.score += 4  # Example value, update from source
            game.puzzles["ladder_puzzle"] = True
            return True
        return False

    # Museum pass puzzle example
    def museum_pass_puzzle(game):
        if not game.puzzles.get("museum_pass_puzzle"):
            print("The guard inspects your pass and lets you in.")
            game.score += 2  # Example value, update from source
            game.puzzles["museum_pass_puzzle"] = True
            return True
        return False

    # Villain defeat puzzle example
    def villain_puzzle(game):
        if not game.puzzles.get("villain_puzzle"):
            print("You have defeated the villain!")
            game.score += 10  # Example value, update from source
            game.puzzles["villain_puzzle"] = True
            return True
        return False

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


# Puzzle handler functions (examples, expand as needed)


# Egg puzzle (for combining egg and canary)
def egg_puzzle(game):
    if not game.puzzles.get("egg_puzzle"):
        print("You open the jewel-encrusted egg. Inside is a golden canary! Score!")
        game.score += 5  # Source: OTVAL for egg/canary
        game.puzzles["egg_puzzle"] = True
        return True
    print("The egg is already open.")
    return False


# Flood control dam puzzle
def dam_puzzle(game):
    if not game.puzzles.get("dam_puzzle"):
        print(
            "You open the flood control dam #3. Water rushes through the sluice gate!"
        )
        game.score += 10  # Source: dam puzzle value
        game.puzzles["dam_puzzle"] = True
        return True
    print("The dam is already open.")
    return False


# Rainbow bridge puzzle
def rainbow_puzzle(game):
    if not game.puzzles.get("rainbow_puzzle"):
        print(
            "The rainbow shimmers and becomes solid. You can cross to the other side!"
        )
        game.score += 4  # Source: rainbow puzzle value
        game.puzzles["rainbow_puzzle"] = True
        return True
    print("The rainbow is already solid.")
    return False


# Trophy case puzzle (placing treasures)
def trophy_case_puzzle(game):
    if not game.puzzles.get("trophy_case_puzzle"):
        print("You place the treasure in the trophy case. Well done!")
        game.score += 10  # Source: trophy case value
        game.puzzles["trophy_case_puzzle"] = True
        return True
    print("The trophy case already contains the treasure.")
    return False


# Grue danger puzzle (entering dark room without light)
def grue_puzzle(game):
    if not game.puzzles.get("grue_puzzle"):
        print("It is pitch dark. You are likely to be eaten by a grue!")
        game.score -= 5  # Source: grue penalty
        game.puzzles["grue_puzzle"] = True
        return True
    print("You are already in danger from the grue.")
    return False


# Ladder puzzle example
def ladder_puzzle(game):
    if not game.puzzles.get("ladder_puzzle"):
        print("With the help of the ladder, you exit the puzzle room!")
        game.score += 4  # Example value, update from source
        game.puzzles["ladder_puzzle"] = True
        return True
    return False


# Museum pass puzzle example
def museum_pass_puzzle(game):
    if not game.puzzles.get("museum_pass_puzzle"):
        print("The guard inspects your pass and lets you in.")
        game.score += 2  # Example value, update from source
        game.puzzles["museum_pass_puzzle"] = True
        return True
    return False


# Villain defeat puzzle example
def villain_puzzle(game):
    if not game.puzzles.get("villain_puzzle"):
        print("You have defeated the villain!")
        game.score += 10  # Example value, update from source
        game.puzzles["villain_puzzle"] = True
        return True
    return False


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


# Puzzle registry: maps triggers to handler functions
PUZZLE_REGISTRY = {
    # Mailbox/leaflet puzzle
    "open mailbox": mailbox_puzzle,
    "read leaflet": mailbox_puzzle,
    # Lantern puzzle
    "turn on lantern": lantern_puzzle,
    "light lantern": lantern_puzzle,
    "turn off lantern": lantern_puzzle,
    # Troll bridge puzzle
    "pay troll": troll_bridge_puzzle,
    "cross bridge": troll_bridge_puzzle,
    # Cyclops puzzle
    "feed cyclops": cyclops_puzzle,
    "give food to cyclops": cyclops_puzzle,
    "put food in cyclops mouth": cyclops_puzzle,
    # Thief puzzle
    "outsmart thief": thief_puzzle,
    "recover treasure from thief": thief_puzzle,
    # Trap door puzzle
    "unlock trap door": trap_door_puzzle,
    "descend trap door": trap_door_puzzle,
    # Volcano puzzle
    "throw item into volcano": volcano_puzzle,
    "sacrifice to volcano": volcano_puzzle,
    # Endgame victory
    "win game": victory_puzzle,
    "endgame victory": victory_puzzle,
    # Egg puzzle
    "open egg": egg_puzzle,
    "combine egg and canary": egg_puzzle,
    # Flood control dam puzzle
    "open dam": dam_puzzle,
    "release water": dam_puzzle,
    # Rainbow bridge puzzle
    "cross rainbow": rainbow_puzzle,
    "solidify rainbow": rainbow_puzzle,
    # Trophy case puzzle
    "place treasure": trophy_case_puzzle,
    "put treasure in case": trophy_case_puzzle,
    # Grue danger
    "enter dark room": grue_puzzle,
    "walk in darkness": grue_puzzle,
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
