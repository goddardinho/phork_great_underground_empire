# command_parser.py
"""
Command parsing logic for the Game class.
This module contains the parse_command function, which operates on a Game instance.
"""


def parse_command(game, command: str):
    cmd = command.strip().lower()
    # Canonical magic words
    magic_words = {
        "xyzzy": "A hollow voice says 'Fool.'",
        "plugh": "Nothing happens.",
        "plover": "A mysterious sound echoes in the distance.",
        "abracadabra": "Nothing up my sleeve!",
        "shazam": "You feel a brief tingle, but nothing else happens.",
    }
    if cmd in magic_words:
        print(magic_words[cmd])
        return True

    # Synonyms and flexible phrasing
    synonyms = {
        "inv": "inventory",
        "invent": "inventory",
        "ex": "examine",
        "inspect": "examine",
        "view": "look",
        "see": "look",
        "walk": "go",
        "run": "go",
        "move": "go",
        "climb": "go",
        "jump": "go",
        "north": "n",
        "south": "s",
        "east": "e",
        "west": "w",
        "northeast": "ne",
        "northwest": "nw",
        "southeast": "se",
        "southwest": "sw",
        "up": "u",
        "down": "d",
    }
    # Replace synonyms at start of command
    for syn, canon in synonyms.items():
        if cmd == syn:
            cmd = canon
            break
        if cmd.startswith(syn + " "):
            cmd = canon + cmd[len(syn):]
            break

    # Flexible phrasing for movement: 'go east', 'walk north', etc.
    if cmd.startswith("go "):
        direction = cmd[3:].strip()
        # Accept both canonical and synonym directions
        dir_map = {
            "north": "n", "south": "s", "east": "e", "west": "w",
            "northeast": "ne", "northwest": "nw", "southeast": "se", "southwest": "sw",
            "up": "u", "down": "d",
            "n": "n", "s": "s", "e": "e", "w": "w", "ne": "ne", "nw": "nw", "se": "se", "sw": "sw", "u": "u", "d": "d"
        }
        direction = dir_map.get(direction, direction)
        # Recurse with canonical direction
        return parse_command(game, direction)

    # Flexible phrasing for 'look at', 'examine the', etc.
    if cmd.startswith("look at "):
        return parse_command(game, "examine " + cmd[8:])
    if cmd.startswith("look in "):
        return parse_command(game, "search " + cmd[8:])
    if cmd.startswith("examine the "):
        return parse_command(game, "examine " + cmd[12:])
    if cmd.startswith("inspect the "):
        return parse_command(game, "examine " + cmd[12:])

    # Canonical snark for silly or meta commands
    silly_commands = [
        "sing", "dance", "sleep", "eat", "drink", "die", "suicide", "pray", "scream", "yell", "jump", "swim", "fly", "teleport", "explode", "explode self", "explode house", "explode mailbox"
    ]
    if cmd in silly_commands:
        snarky_silly = [
            "That is not a productive use of your time.",
            "You must be joking.",
            "Nothing happens.",
            "You feel a bit silly.",
            "This is not the time or place for that.",
            "You can't do that here.",
        ]
        import random
        print(random.choice(snarky_silly))
        return True
    # Canonical snark for bodily functions and cursewords
    bodily_functions = [
        "burp",
        "fart",
        "poop",
        "pee",
        "vomit",
        "spit",
        "puke",
        "defecate",
        "urinate",
    ]
    cursewords = [
        "damn",
        "hell",
        "shit",
        "fuck",
        "bitch",
        "bastard",
        "ass",
        "crap",
        "dick",
        "piss",
        "bollocks",
        "bugger",
        "arse",
        "wank",
        "twat",
        "cunt",
    ]
    if cmd in bodily_functions:
        snarky_bodily = [
            "Such behavior is unbecoming of an adventurer!",
            "Really? In public?",
            "You feel a bit embarrassed.",
            "This is a high-class establishment!",
            "You must be joking.",
            "That is not necessary right now.",
        ]
        import random
        print(random.choice(snarky_bodily))
        return True
    if cmd in cursewords:
        snarky_curse = [
            "Watch your language!",
            "There is no need to be rude.",
            "Such language in a place like this!",
            "The parser blushes at your words.",
            "You must be joking.",
        ]
        import random
        print(random.choice(snarky_curse))
        return True
    """Parse and execute a command string for the given Game instance."""
    cmd = command.strip().lower()
    # Save command (canonical: snark if already saved)
    if cmd == "save":
        if getattr(game, "already_saved", False):
            print("You have already saved recently.")
        else:
            game.save_game()
            game.already_saved = True
            print("Game saved.")
        return True
    # Help command (canonical: snark if help is repeated)
    if cmd in ["help", "h", "?", "commands"]:
        if getattr(game, "helped", False):
            print("You seem to need a lot of help.")
        else:
            from help_utils import show_help

            show_help()
            game.helped = True
        return True
    # Thief random encounter tick
    if game.thief_cooldown > 0:
        game.thief_cooldown -= 1
    else:
        game.tick_thief()
    game.maybe_thief_event()
    cmd = command.strip().lower()
    # Canonical: put <item> in <container>
    # Canonical: put <item> in <container> (snark, flexible phrasing)
    if cmd.startswith("put ") and " in " in cmd:
        parts = cmd.split(" in ", 1)
        item_name = parts[0][4:].strip()
        container_name = parts[1].strip()
        item = next((o for o in game.inventory if o.name.lower() == item_name), None)
        room = game.rooms.get(game.current_room)
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
            print(f"You don't have a {item_name} to put. Are you trying to be funny?")
            return True
        if not container:
            print(f"You can't put things in the {container_name} here.")
            return True
        if not container.attributes.get("open", False):
            print(f"The {container.name} is closed. You must open it first.")
            return True
        game.inventory.remove(item)
        container.attributes.setdefault("contents", []).append(item)
        print(f"You put the {item.name} in the {container.name}. It fits nicely.")
        return True
    # Canonical: place <item> on <surface>
    if cmd.startswith("place ") and " on " in cmd:
        parts = cmd.split(" on ", 1)
        item_name = parts[0][6:].strip()
        surface_name = parts[1].strip()
        item = next((o for o in game.inventory if o.name.lower() == item_name), None)
        room = game.rooms.get(game.current_room)
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
            print(
                f"You don't have a {item_name} to place. Are you trying to place air?"
            )
            return True
        if not surface:
            print(f"You can't place things on the {surface_name} here.")
            return True
        game.inventory.remove(item)
        if room:
            room.objects.append(item)
            print(
                f"You place the {item.name} on the {surface.name}. It looks out of place."
            )
        else:
            print("There is no room to place the item in. You must be joking.")
        return True
    # Canonical: unlock <container> with <key>
    if cmd.startswith("unlock ") and " with " in cmd:
        parts = cmd.split(" with ", 1)
        container_name = parts[0][7:].strip()
        key_name = parts[1].strip()
        room = game.rooms.get(game.current_room)
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
        key = next((o for o in game.inventory if o.name.lower() == key_name), None)
        if not container:
            print(f"You can't unlock the {container_name} here.")
            return True
        if not key:
            print(f"You don't have the right key for the {container_name}.")
            return True
        if not container.attributes.get("locked", False):
            print(f"The {container.name} is already unlocked. Try opening it.")
            return True
        container.attributes["locked"] = False
        container.attributes["open"] = True
        print(f"You unlock the {container.name} with the {key.name}. Success!")
        return True
    # Canonical: lock <container>
    if cmd.startswith("lock "):
        container_name = cmd[5:].strip()
        room = game.rooms.get(game.current_room)
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
            print(f"You can't lock the {container_name} here.")
            return True
        elif not container.attributes.get("openable", False):
            print(f"The {container.name} cannot be locked. Are you serious?")
            return True
        elif container.attributes.get("locked", False):
            print(f"The {container.name} is already locked. Try unlocking it first.")
            return True
        else:
            container.attributes["locked"] = True
            container.attributes["open"] = False
            print(f"You lock the {container.name}. It is now secure.")
            return True
    # Canonical: tie <object> to <object>
    if cmd.startswith("tie ") and " to " in cmd:
        parts = cmd.split(" to ", 1)
        obj_name = cmd.split(" ", 1)[1]
        room = game.rooms.get(game.current_room)
        obj = next(
            (
                o
                for o in (game.inventory + (room.objects if room else []))
                if o.name.lower() == obj_name
            ),
            None,
        )
        if obj:
            if obj.attributes.get("tieable", False):
                print(f"You tie the {obj.name} securely.")
                obj.attributes["tied"] = True
                return True
            if obj.attributes.get("bunch", False) or obj.attributes.get(
                "collective", False
            ):
                print(f"You can't tie the {obj.name} as a whole.")
                return True
            print(f"You can't tie the {obj.name}.")
            return True
        print(f"There is no {obj_name} here to tie.")
        return True
        return True
    # Canonical: turn <object>
    if cmd == "turn":
        print("Turn what? Be more specific.")
        return True
    if cmd.startswith("turn "):
        obj_name = cmd[5:].strip()
        room = game.rooms.get(game.current_room)
        obj = None
        if room:
            obj = next((o for o in room.objects if o.name.lower() == obj_name), None)
        if not obj:
            print(f"There is no {obj_name} here to turn. Are you hallucinating?")
            return True
        print(f"You turn the {obj.name}. It resists your efforts.")
        return True
    # Canonical: search <container> or room
    if cmd.startswith("search "):
        obj_name = cmd[7:].strip()
        room = game.rooms.get(game.current_room)
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
                print(f"The {obj.name} is closed. Try opening it first.")
            return True
        # If not a container, search the room
        if room and obj_name in [room.id.lower(), "room", "area"]:
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
                print("You search the room but find nothing of interest.")
            return True
        elif not room:
            print("There is no room to search. Are you lost?")
            return True
        print(
            f"You find nothing special about the {obj_name}. Maybe try something else."
        )
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
            "Violence isn't the answer.",
            "The {name} resists your efforts.",
        ]
        verb = cmd.split(" ")[0]
        import random

        print(random.choice(snarky_pushpull).format(verb=verb, name=obj_name))
        return True

    # Object interaction: use
    if cmd.startswith("use "):
        obj_name = cmd.split(" ", 1)[1]
        snarky_use = [
            "You can't use that here.",
            "Nothing happens.",
            "Use the {name}? How?",
            "You must be joking.",
            "The {name} doesn't seem to do anything.",
        ]
        import random

        print(random.choice(snarky_use).format(name=obj_name))
        return True

    # Object interaction: hang/place
    if any(cmd.startswith(x + " ") for x in ["hang", "place"]):
        obj_name = cmd.split(" ", 1)[1]
        snarky_hangplace = [
            "You can't do that.",
            "There's nowhere to hang the {name} here.",
            "Placing the {name} accomplishes nothing.",
            "You must be joking.",
            "The {name} is not meant to be hung.",
        ]
        import random

        print(random.choice(snarky_hangplace).format(name=obj_name))
        return True

    # Object interaction: examine (synonym for look)
    if cmd.startswith("examine "):
        obj_name = cmd.split(" ", 1)[1]
        from object_actions import object_action

        # Try to find object in room or inventory
        room = game.rooms.get(game.current_room)
        obj = None
        if room:
            obj = next((o for o in room.objects if o.name.lower() == obj_name), None)
        if not obj:
            obj = next((o for o in game.inventory if o.name.lower() == obj_name), None)
        # Actor inventory search
        if obj and obj.attributes.get("actor", False) and hasattr(obj, "inventory"):
            if obj.inventory:
                print(
                    f"You examine the {obj.name} and find: {', '.join([item.name for item in obj.inventory])}."
                )
            else:
                print(f"You examine the {obj.name} but find nothing of interest.")
            return True
        # Indescribable
        if obj and obj.attributes.get("indescribable", False):
            print(f"You can't make out any details about the {obj.name}.")
            return True
        if object_action(game, "look", obj_name):
            return True
        print(f"You see nothing special about the {obj_name}. Maybe try searching it.")
        return True
    # Canonical NPC interactions
    # Modular two-way combat for attack/fight/kill/stab/hit
    combat_actions = ["fight ", "attack ", "kill ", "stab ", "hit "]
    for prefix in combat_actions:
        if cmd.startswith(prefix):
            npc_name = cmd[len(prefix) :].strip()
            room = game.rooms.get(game.current_room)
            npc = next(
                (n for n in getattr(room, "npcs", []) if n.name.lower() == npc_name),
                None,
            )
            # Trytake/villain resist
            if not npc:
                # Check objects for villain/trytake
                obj = None
                if room:
                    obj = next(
                        (o for o in room.objects if o.name.lower() == npc_name),
                        None,
                    )
                if obj and obj.attributes.get("villain", False):
                    print(f"The {obj.name} resists your attack!")
                    return True
                if obj and obj.attributes.get("trytake", False):
                    print(f"The {obj.name} seems to resist your attack.")
                    return True
                print(f"There is no {npc_name} here to attack.")
                return True
            from combat import CombatEngine

            result = CombatEngine.combat_round(game.player, npc)
            print(result)
            if game.player.is_dead():
                game.game_over()
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
        if cmd == action:
            # No target provided
            if action == "hello":
                import random

                hellos = [
                    "You say hello to the world.",
                    "Nothing happens.",
                    "You greet the void.",
                    "You feel a bit silly saying hello to nobody.",
                ]
                print(random.choice(hellos))
            else:
                print(f"{action.capitalize()} whom?")
            return True
        if cmd.startswith(prefix):
            npc_name = cmd[len(prefix) :].strip()
            room = game.rooms.get(game.current_room)
            npc = next(
                (n for n in getattr(room, "npcs", []) if n.name.lower() == npc_name),
                None,
            )
            if npc:
                print(npc.interact(game, action=action))
            else:
                print(f"There is no {npc_name} here to {action}.")
            return True
    # Check for player death after any command
    if game.player.is_dead():
        game.handle_death()
        return True
    # Give <item> <npc>
    if cmd.startswith("give "):
        parts = cmd.split(" ")
        if len(parts) == 3:
            item_name, npc_name = parts[1], parts[2]
            item = next(
                (o for o in game.inventory if o.name.lower() == item_name), None
            )
            room = game.rooms.get(game.current_room)
            npc = next(
                (n for n in getattr(room, "npcs", []) if n.name.lower() == npc_name),
                None,
            )
            if npc and item:
                print(npc.interact(game, action="give", item=item))
                game.inventory.remove(item)
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
                (o for o in game.inventory if o.name.lower() == item_name), None
            )
            room = game.rooms.get(game.current_room)
            npc = next(
                (n for n in getattr(room, "npcs", []) if n.name.lower() == npc_name),
                None,
            )
            if npc and item:
                print(npc.interact(game, action="bribe", item=item))
                game.inventory.remove(item)
            else:
                print("Bribe failed: check NPC and item names.")
        else:
            print("Usage: bribe <npc> <item>")
        return True
    # Canonical commands from MUD source
    if cmd in ["quit", "exit"]:
        confirm = input("Are you sure you want to quit? (y/n): ").strip().lower()
        if confirm in ["y", "yes"]:
            print("Thanks for playing! May your adventures continue.")
            return False
        else:
            print("Resuming your adventure.")
            return True
    elif cmd in ["look", "l"]:
        print("You look around...")
        game.look()
        print("You see exits: " + ", ".join(game.rooms[game.current_room].exits))
        return True
    # Canonical direction commands always recognized
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
        room = game.rooms.get(game.current_room)
        if not room:
            print("You can't go that way.")
            return True
        locked_exits = getattr(room, "locked_exits", {})
        # Check if direction is a valid exit
        if direction in room.exits:
            if direction in locked_exits and locked_exits[direction]:
                print(f"The door to {direction} is locked.")
                return True
            game.move(direction)
            return True
        else:
            print("You can't go that way.")
            return True
    elif cmd in ["inventory", "i"]:
        game.show_inventory()
        return True
    # Object interaction: get/take
    elif cmd.startswith("get ") or cmd.startswith("take "):
        obj_name = cmd.split(" ", 1)[1]
        room = (
            game.rooms.get(game.current_room)
            if game.current_room and game.current_room in game.rooms
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
                            game.inventory.append(leaflet_obj)
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
                if obj_weight == game.BIGFIX:
                    obj_weight = 0
                if (
                    not game.demo_mode
                    and game.get_inventory_weight() + obj_weight > game.LOAD_MAX
                ):
                    print(
                        f"You can't carry the {obj.name}; it's too heavy or you're overloaded."
                    )
                    continue
                game.inventory.append(obj)
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
                        if obj_weight == game.BIGFIX:
                            obj_weight = 0
                        if (
                            not game.demo_mode
                            and game.get_inventory_weight() + obj_weight > game.LOAD_MAX
                        ):
                            print(
                                f"You can't carry the {item.name}; it's too heavy or you're overloaded."
                            )
                            continue
                        obj.remove_object(item)
                        game.inventory.append(item)
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
                            game.inventory.append(leaflet_obj)
                            print("You take the leaflet.")
                            return True
                    print("You can't take the leaflet unless the mailbox is open.")
                    return True
                # Prevent taking dangerous, burning, sacred, or villain objects, or those that resist being taken
                if obj.attributes.get("dangerous", False):
                    print(
                        f"You recoil from the {obj.name}; it looks dangerous to touch!"
                    )
                    return True
                if obj.attributes.get("burning", False):
                    print(f"You can't take the {obj.name} while it's burning!")
                    return True
                if obj.attributes.get("sacred", False):
                    print(
                        f"You feel an invisible force prevents you from taking the {obj.name}."
                    )
                    return True
                if obj.attributes.get("collective", False):
                    print(
                        f"You can't take the {obj.name} as a whole; try taking individual items."
                    )
                    return True
                if obj.attributes.get("villain", False):
                    print(f"The {obj.name} resists your attempt to take it!")
                    return True
                if obj.attributes.get("trytake", False):
                    print(f"The {obj.name} seems to resist being taken.")
                    return True
                if not obj.attributes.get("takeable", True) or not obj.attributes.get(
                    "portable", True
                ):
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
                if obj_weight == game.BIGFIX:
                    obj_weight = 0
                if (
                    not game.demo_mode
                    and game.get_inventory_weight() + obj_weight > game.LOAD_MAX
                ):
                    print(f"You cannot carry the {obj.name}. Your load is too heavy.")
                    return True
                game.inventory.append(obj)
                room.objects.remove(obj)
                # Set 'touched' attribute when object is taken (Zork TOUCHBIT)
                obj.attributes["touched"] = True
                print(f"You take the {obj.name}.")
                if obj.name.lower() in [
                    "treasure chest",
                    "treasure",
                    "jewel",
                    "gold",
                    "diamond",
                ]:
                    game.score += 10  # Award points for treasures
                    print("You have found a treasure! (+10 points)")
                else:
                    game.score += 1  # Minor score for other items
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
                        if obj_weight == game.BIGFIX:
                            obj_weight = 0
                        if (
                            not game.demo_mode
                            and game.get_inventory_weight() + obj_weight > game.LOAD_MAX
                        ):
                            print(
                                f"You cannot carry the {item.name}. Your load is too heavy."
                            )
                            return True
                        container.remove_object(item)
                        game.inventory.append(item)
                        print(f"You take the {item.name} from the {container.name}.")
                        game.score += 1
                        return True
            print(f"There is no {obj_name} here.")
        else:
            print("No room loaded.")
        return True
    # Object interaction: drop/put/throw
    elif any(cmd.startswith(x + " ") for x in ["drop", "put", "throw"]):
        obj_name = cmd.split(" ", 1)[1]
        if obj_name == "all":
            if not game.inventory:
                print("You have nothing to drop.")
                return True
            room = (
                game.rooms.get(game.current_room)
                if game.current_room and game.current_room in game.rooms
                else None
            )
            if not room:
                print("No room loaded.")
                return True
            for obj in list(game.inventory):
                game.inventory.remove(obj)
                room.objects.append(obj)
                print(f"You drop the {obj.name}.")
            return True
        obj = next((o for o in game.inventory if o.name.lower() == obj_name), None)
        if obj:
            game.inventory.remove(obj)
            room = (
                game.rooms.get(game.current_room)
                if game.current_room and game.current_room in game.rooms
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
        obj = next((o for o in game.inventory if o.name.lower() == obj_name), None)
        if not obj:
            room = game.rooms.get(game.current_room)
            if room:
                obj = next(
                    (o for o in room.objects if o.name.lower() == obj_name), None
                )
        if obj:
            if obj.attributes.get("locked", False):
                print(f"The {obj.name} is locked.")
                return True
            if obj.attributes.get("openable", False) or obj.attributes.get(
                "door", False
            ):
                if obj.attributes.get("open", False):
                    print(f"The {obj.name} is already open.")
                else:
                    obj.attributes["open"] = True
                    print(f"You open the {obj.name}.")
                return True
            print(f"You can't open the {obj.name}.")
            return True
        print(f"There is no {obj_name} here to open.")
        return True

    # ...existing code...

    # Catch-all for unknown commands (move to very end of function)
    import random

    unknowns = [
        "I don't understand that command.",
        "I don't know that word.",
        "You must be joking.",
        "That command makes no sense.",
        "Try something else.",
        "What are you trying to do?",
    ]
    print(random.choice(unknowns))
    return True
