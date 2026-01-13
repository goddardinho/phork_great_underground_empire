def show_help():
    """Display available commands with descriptions and usage examples."""
    commands = [
        {"cmd": "look", "desc": "Examine your surroundings.", "usage": "look or l"},
        {"cmd": "go <direction>", "desc": "Move in a direction (north, south, east, west, up, down).", "usage": "go north"},
        {"cmd": "inventory", "desc": "Show your inventory.", "usage": "inventory or i"},
        {"cmd": "get <object>", "desc": "Pick up an object.", "usage": "get lantern"},
        {"cmd": "drop <object>", "desc": "Drop an object from your inventory.", "usage": "drop sword"},
        {"cmd": "open <object>", "desc": "Open a container or door.", "usage": "open mailbox"},
        {"cmd": "close <object>", "desc": "Close a container or door.", "usage": "close mailbox"},
        {"cmd": "read <object>", "desc": "Read something readable.", "usage": "read leaflet"},
        {"cmd": "eat <object>", "desc": "Eat something edible.", "usage": "eat food"},
        {"cmd": "drink <object>", "desc": "Drink something drinkable.", "usage": "drink water"},
        {"cmd": "climb <object>", "desc": "Climb something climbable.", "usage": "climb tree"},
        {"cmd": "jump", "desc": "Jump in place or over something.", "usage": "jump"},
        {"cmd": "swim", "desc": "Swim if possible.", "usage": "swim"},
        {"cmd": "attack <target>", "desc": "Attack a creature or NPC.", "usage": "attack troll"},
        {"cmd": "examine <object>", "desc": "Examine an object closely.", "usage": "examine sword"},
        {"cmd": "search <object>", "desc": "Search an object or area.", "usage": "search chest"},
        {"cmd": "unlock <direction|door>", "desc": "Unlock an exit or door.", "usage": "unlock east"},
        {"cmd": "lock <direction|door>", "desc": "Lock an exit or door.", "usage": "lock west"},
        {"cmd": "turn <object>", "desc": "Turn something (like a key).", "usage": "turn key"},
        {"cmd": "push <object>", "desc": "Push an object.", "usage": "push button"},
        {"cmd": "pull <object>", "desc": "Pull an object.", "usage": "pull lever"},
        {"cmd": "light <object>", "desc": "Light an object (like a lantern).", "usage": "light lantern"},
        {"cmd": "extinguish <object>", "desc": "Extinguish a light source.", "usage": "extinguish lantern"},
        {"cmd": "wear <object>", "desc": "Wear an item.", "usage": "wear cloak"},
        {"cmd": "remove <object>", "desc": "Remove a worn item.", "usage": "remove cloak"},
        {"cmd": "save", "desc": "Save your game progress.", "usage": "save"},
        {"cmd": "restore", "desc": "Restore a saved game.", "usage": "restore"},
        {"cmd": "restart", "desc": "Restart the game.", "usage": "restart"},
        {"cmd": "score", "desc": "Show your current score.", "usage": "score"},
        {"cmd": "wait", "desc": "Wait for a turn.", "usage": "wait"},
        {"cmd": "listen", "desc": "Listen for sounds.", "usage": "listen"},
        {"cmd": "help", "desc": "Show this help message.", "usage": "help"},
        {"cmd": "quit", "desc": "Quit the game.", "usage": "quit or exit"},
    ]
    print("\nAvailable Commands:")
    for c in commands:
        print(f"  {c['cmd']:<18} - {c['desc']}\n    Usage: {c['usage']}")
    print("\nType commands as shown. Some commands accept synonyms or abbreviations (e.g., 'l' for 'look', 'i' for 'inventory').")
