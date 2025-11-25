from objects import GameObject
from containers import Container

def object_action(game, cmd, obj_name):
    # Mailbox actions
    if obj_name == "mailbox":
        room = game.rooms.get(game.current_room)
        mailbox = next((o for o in room.objects if o.name.lower() == "mailbox"), None) if room else None
        if not mailbox:
            print("There is no mailbox here.")
            return True
        if cmd == "open":
            print(mailbox.open())
            game.mailbox_open = mailbox.attributes.get("open", False)
            game.describe_current_room()
        elif cmd == "look":
            print(mailbox.look_inside())
        elif cmd == "close":
            if not mailbox.attributes.get("open", False):
                print("The mailbox is already closed.")
            else:
                mailbox.attributes["open"] = False
                print("You close the mailbox.")
            game.mailbox_open = mailbox.attributes.get("open", False)
        else:
            print("You can't do that to the mailbox.")
        return True

    # Leaflet actions
    if obj_name == "leaflet":
        if cmd == "take":
            room = game.rooms.get(game.current_room)
            mailbox = next((o for o in room.objects if o.name.lower() == "mailbox"), None) if room else None
            if game.leaflet_taken:
                print("You already have the leaflet.")
            elif mailbox and mailbox.attributes.get("open", False):
                # Find leaflet in mailbox contents
                contents = mailbox.attributes.get("contents", [])
                leaflet_obj = next((o for o in contents if o.name.lower() == "leaflet"), None)
                if leaflet_obj:
                    mailbox.remove_object(leaflet_obj)
                    game.inventory.append(leaflet_obj)
                    game.leaflet_taken = True
                    print("You take the leaflet.")
                else:
                    print("There is no leaflet in the mailbox.")
            else:
                print("You can't take the leaflet unless the mailbox is open.")
        elif cmd == "read":
            leaflet_obj = next((o for o in game.inventory if o.name.lower() == "leaflet"), None)
            if leaflet_obj:
                print(leaflet_obj.description)
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
