#!/usr/bin/env python3
"""
Test script for dynamic room descriptions
"""

from src.game import GameEngine


def test_dynamic_descriptions():
    """Test the dynamic room description functionality."""
    print("=== Testing Dynamic Room Descriptions ===")
    print()
    
    # Create a simple test game
    print("Creating test game...")
    game = GameEngine(use_mud_files=False)  # Use simple test world
    
    print("✓ Game created")
    print()
    
    # Test initial room (should show full description on first entry)
    print("1. Testing initial room appearance (should be full description):")
    current_room = game.world.get_room(game.player.current_room)
    print(f"   Room visited status: {current_room.visited}")
    print(f"   Player brief mode: {game.player.brief_mode}")
    print()
    
    game._look_around()
    print()
    print(f"   After _look_around, room visited: {current_room.visited}")
    print()
    
    # Test same room again (should show same because brief mode is off by default)
    print("2. Testing same room again (brief mode off, should show full):")
    game._look_around()
    print()
    
    # Enable brief mode and test again
    print("3. Testing with brief mode enabled (should show short description):")
    game.player.brief_mode = True
    game._look_around()
    print()
    
    # Test explicit look command (should override brief mode)
    print("4. Testing explicit look command (should override brief mode):")
    game._look_around(force_verbose=True)
    print()
    
    # Test movement to new room
    print("5. Testing movement to new room (should show full description even in brief mode):")
    # Move north
    game.player.move_to_room("NHOUS")
    new_room = game.world.get_room("NHOUS")
    print(f"   New room visited before _look_around: {new_room.visited}")
    game._look_around()
    print(f"   New room visited after _look_around: {new_room.visited}")
    print()
    
    # Visit same new room again in brief mode 
    print("6. Testing same new room again (brief mode on, should be short):")
    game._look_around()
    print()
    
    # Test verbose mode
    print("7. Testing verbose mode (should disable brief descriptions):")
    game.player.brief_mode = False  # Turn off brief mode
    game._look_around()
    print()
    
    print("✓ Dynamic description tests completed!")


if __name__ == "__main__":
    test_dynamic_descriptions()