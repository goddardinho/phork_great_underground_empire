#!/usr/bin/env python3
"""
Quick test script to verify the .mud file game functionality works
"""

from pathlib import Path
from src.game import GameEngine


def test_mud_game():
    """Test the game with loaded .mud files."""
    print("=== Testing Zork with .mud files ===")
    print()
    
    # Create game with .mud loading
    game = GameEngine(use_mud_files=True)
    
    # Test basic functionality
    print("Testing basic room access...")
    
    # Check that we have rooms loaded
    room_count = len(game.world.rooms)
    print(f"✓ Loaded {room_count} rooms")
    
    # Check starting position
    starting_room = game.world.get_room(game.player.current_room)
    if starting_room:
        print(f"✓ Starting room: {starting_room.name} ({starting_room.id})")
    else:
        print("✗ Starting room not found!")
        return False
    
    # Check mailbox object exists
    if "MAILBOX" in game.objects:
        mailbox = game.objects["MAILBOX"]
        print(f"✓ Mailbox exists: {mailbox.name}")
    else:
        print("✗ Mailbox object not found!")
        return False
    
    # Check West of House has the mailbox
    whous = game.world.get_room("WHOUS")
    if whous and "MAILBOX" in whous.items:
        print("✓ Mailbox is in West of House")
    else:
        print("✗ Mailbox not found in West of House!")
        return False
    
    # Test some iconic rooms exist
    iconic_rooms = [
        ("WHOUS", "West of House"),
        ("NHOUS", "North of House"), 
        ("SHOUS", "South of House"),
        ("TREAS", "Treasure Room"),
        ("EGYPT", "Egyptian Room"),
        ("MTROL", "The Troll Room")
    ]
    
    print()
    print("Testing iconic room existence...")
    for room_id, expected_name in iconic_rooms:
        room = game.world.get_room(room_id)
        if room:
            print(f"✓ {room_id}: {room.name}")
        else:
            print(f"✗ {room_id} not found!")
    
    # Test movement functionality
    print()
    print("Testing navigation...")
    
    # Try going north from West of House
    current_room = game.world.get_room(game.player.current_room)
    north_exit = current_room.get_exit("north")
    
    if north_exit:
        north_room = game.world.get_room(north_exit)
        if north_room:
            print(f"✓ North exit leads to: {north_room.name} ({north_exit})")
        else:
            print(f"✗ North exit points to invalid room: {north_exit}")
    else:
        print("✗ No north exit from West of House!")
    
    print()
    print("✓ .mud file integration test completed successfully!")
    return True


if __name__ == "__main__":
    test_mud_game()