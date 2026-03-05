#!/usr/bin/env python3
"""
Test script for ambiguity resolution system
"""

from src.game import GameEngine


def test_disambiguation():
    """Test the disambiguation system with multiple similar objects."""
    print("=== Testing Ambiguity Resolution System ===")
    print()
    
    # Create test game
    print("Creating test game with ambiguous objects...")
    game = GameEngine(use_mud_files=False)
    
    print("✓ Game created")
    print()
    
    # Move to temple where there are two knives
    print("1. Moving to Ancient Temple (contains two knives):")
    game.player.move_to_room("TEMPLE")
    game._look_around()
    print()
    
    # Try to examine a knife (should trigger disambiguation)
    print("2. Testing 'examine knife' (should show disambiguation):")
    game._process_command("examine knife")
    print()
    
    # Test disambiguation response with number
    if game.player.awaiting_disambiguation:
        print("3. Testing disambiguation response with number '1':")
        game._process_command("1")
        print()
    
    # Reset and test disambiguation with descriptive text
    print("4. Testing 'take knife' and responding with 'silver':")
    game._process_command("take knife")
    print()
    
    if game.player.awaiting_disambiguation:
        print("5. Responding with 'silver':")
        game._process_command("silver")
        print()
    
    # Test inventory to see what we picked up
    print("6. Checking inventory:")
    game._handle_inventory()
    print()
    
    # Move to cave where there are two boxes
    print("7. Moving to Dark Cave (contains two boxes). First, light torch:")
    
    # Get torch and matches from forest first
    game.player.move_to_room("FOREST")
    game._process_command("take torch")
    game._process_command("take matches")
    game._process_command("light torch")
    
    # Now go to cave
    game.player.move_to_room("CAVE")
    game._look_around()
    print()
    
    # Try to take a box
    print("8. Testing 'take box' (should show disambiguation):")
    game._process_command("take box")
    print()
    
    # Test canceling disambiguation
    if game.player.awaiting_disambiguation:
        print("9. Testing cancellation with 'cancel':")
        game._process_command("cancel")
        print()
    
    # Test disambiguation with partial match
    print("10. Testing 'examine box' and responding with 'wooden':")
    game._process_command("examine box")
    print()
    
    if game.player.awaiting_disambiguation:
        print("11. Responding with 'wooden':")
        game._process_command("wooden")
        print()
    
    print("✓ Disambiguation system tests completed!")


def test_disambiguation_states():
    """Test the internal state management of disambiguation."""
    print()
    print("=== Testing Disambiguation State Management ===")
    print()
    
    game = GameEngine(use_mud_files=False)
    
    # Test finding all objects
    game.player.move_to_room("TEMPLE")
    
    print("1. Testing _find_all_objects for 'knife':")
    matches = game._find_all_objects("knife")
    for i, obj in enumerate(matches):
        print(f"   {i+1}. {obj.name} ({obj.id})")
    print()
    
    print("2. Testing _find_object with multiple matches:")
    result = game._find_object("knife") 
    print(f"   Result: {result}")
    print(f"   Awaiting disambiguation: {game.player.awaiting_disambiguation}")
    print(f"   Disambiguation options: {len(game.player.disambiguation_options)}")
    print()
    
    # Test location descriptions
    print("3. Testing object location descriptions:")
    for obj in game.player.disambiguation_options:
        location_desc = game._get_object_location_description(obj)
        print(f"   {obj.name}: {location_desc}")
    
    # Clear disambiguation
    game._clear_disambiguation()
    print()
    print("4. After clearing disambiguation:")
    print(f"   Awaiting disambiguation: {game.player.awaiting_disambiguation}")
    print(f"   Disambiguation options: {len(game.player.disambiguation_options)}")
    
    print()
    print("✓ State management tests completed!")


if __name__ == "__main__":
    test_disambiguation()
    test_disambiguation_states()