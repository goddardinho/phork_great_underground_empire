#!/usr/bin/env python3
"""
Automated test: Validate canonical object interactions for all Zork objects.
Checks examine, take, open, and container state transitions for canonical objects.
"""

from src.game import GameEngine

def test_canonical_object_interactions():
    print("\n🔬 TEST: CANONICAL OBJECT INTERACTIONS\n" + "="*40)
    game = GameEngine(use_mud_files=True)
    om = game.object_manager
    world = game.world
    player = game.player

    # Helper: Move player to a room
    def goto(room_id):
        player.current_room = room_id

    # Test nest/egg canonical sequence
    goto("TREE")
    nest = om.get_object("NEST")
    egg = om.get_object("EGG")
    assert nest.is_open(), "Nest should start open"
    assert egg in [om.get_object(i) for i in nest.get_contents()], "Egg should be in nest"

    # Examine nest (should show open, contains egg)
    print("Examine nest:")
    game._handle_examine(type('Cmd', (), {'noun': 'nest'})())

    # Take egg
    print("Take egg:")
    game._handle_take(type('Cmd', (), {'noun': 'egg'})())
    assert egg.id in player.inventory, "Egg should be in inventory after take"
    assert egg.id not in nest.get_contents(), "Egg should be removed from nest after take"

    # Examine egg (should be closed, empty)
    print("Examine egg:")
    game._handle_examine(type('Cmd', (), {'noun': 'egg'})())
    assert not egg.is_open(), "Egg should start closed"
    assert egg.get_contents() == [], "Egg should be empty after take"

    # Open egg
    print("Open egg:")
    game._handle_open(type('Cmd', (), {'noun': 'egg'})())
    assert egg.is_open(), "Egg should be open after open command"
    assert egg.get_contents() == [], "Egg should still be empty after open"

    # Add more canonical object interaction tests as needed...
    print("\nAll canonical object interaction tests passed!\n")

if __name__ == "__main__":
    test_canonical_object_interactions()
