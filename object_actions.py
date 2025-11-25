from entities import GameObject

def object_action(game, cmd, obj_name):
    # Mailbox actions
    if obj_name == "mailbox":
        if cmd == "open":
            if game.mailbox_open:
                print("The mailbox is already open.")
            else:
                game.mailbox_open = True
                print("You open the mailbox.")
        elif cmd == "look":
            if game.mailbox_open:
                if not game.leaflet_taken:
                    print("There is a leaflet inside the mailbox.")
                else:
                    print("The mailbox is empty.")
            else:
                print("The mailbox is closed.")
        elif cmd == "close":
            if not game.mailbox_open:
                print("The mailbox is already closed.")
            else:
                game.mailbox_open = False
                print("You close the mailbox.")
        else:
            print("You can't do that to the mailbox.")
        return True

    # Leaflet actions
    if obj_name == "leaflet":
        if cmd == "take":
            if game.mailbox_open and not game.leaflet_taken:
                game.leaflet_taken = True
                game.inventory.append(GameObject("Leaflet", "A small leaflet with writing on it."))
                print("You take the leaflet.")
            elif game.leaflet_taken:
                print("You already have the leaflet.")
            else:
                print("You can't take the leaflet unless the mailbox is open.")
        elif cmd == "read":
            if any(o.name.lower() == "leaflet" for o in game.inventory):
                print("Welcome to Zork! Your mission is to find the treasures and escape alive.")
            else:
                print("You don't have the leaflet.")
        else:
            print("You can't do that to the leaflet.")
        return True

    # Lantern actions
    if obj_name == "lantern":
        if cmd == "light":
            if game.lantern_lit:
                print("The lantern is already lit.")
            else:
                game.lantern_lit = True
                print("You light the lantern. The darkness is banished.")
        elif cmd == "extinguish":
            if not game.lantern_lit:
                print("The lantern is already out.")
            else:
                game.lantern_lit = False
                print("You extinguish the lantern. The room grows dark.")
        else:
            print("You can't do that to the lantern.")
        return True

    return False
