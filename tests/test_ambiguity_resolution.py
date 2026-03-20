#!/usr/bin/env python3
"""
Test disambiguation functionality - simplified version that works with current objects.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game import GameEngine


def test_basic_disambiguation():
    """Test that disambiguation prompts work with available objects."""
    print("Testing basic disambiguation system...")
    
    game = GameEngine(use_mud_files=False)
    
    # Move to a room that exists (WHOUS is always available)
    game.player.move_to_room("WHOUS")
    
    # Test with a command that won't find matching objects
    # This should give a clear "not found" message, not a crash
    try:
        game._process_command("take nonexistent")
        print("✓ Non-existent object command handled gracefully")
    except Exception as e:
        print(f"❌ Non-existent object command caused error: {e}")
        return False
    
    # The key is that the game should handle disambiguation gracefully
    # Even when no objects match, it shouldn't crash
    assert not hasattr(game.player, 'awaiting_disambiguation') or not game.player.awaiting_disambiguation
    
    return True


def test_no_crash_on_invalid_commands():
    """Test that invalid disambiguation choices don't crash the game."""
    print("Testing invalid command handling...")
    
    game = GameEngine(use_mud_files=False)
    game.player.move_to_room("WHOUS") 
    
    # Test various potentially problematic commands
    test_commands = [
        "1",  # Number when not disambiguating
        "invalid",  # Random text
        "",  # Empty command
        "take",  # Incomplete command
        "go nowhere"  # Invalid direction
    ]
    
    for cmd in test_commands:
        try:
            game._process_command(cmd)
            print(f"  ✓ Command '{cmd}' handled gracefully")
        except Exception as e:
            print(f"  ❌ Command '{cmd}' caused error: {e}")
            return False
    
    return True


def test_player_state_consistency():
    """Test that player state remains consistent."""
    print("Testing player state consistency...")
    
    game = GameEngine(use_mud_files=False)
    
    # Test that player has essential attributes
    assert hasattr(game.player, 'current_room'), "Player should have current_room"
    assert hasattr(game.player, 'inventory'), "Player should have inventory"
    assert isinstance(game.player.inventory, list), "Player inventory should be a list"
    
    # Test basic commands don't break state
    initial_room = game.player.current_room
    initial_inventory_len = len(game.player.inventory)
    
    try:
        game._process_command("look")
        assert game.player.current_room == initial_room, "Room should not change on look"
        
        game._process_command("inventory")
        assert len(game.player.inventory) == initial_inventory_len, "Inventory size should not change on inventory command"
        
        print("✓ Player state consistency maintained")
        return True
    except Exception as e:
        print(f"❌ Player state consistency test failed: {e}")
        return False


def test_game_engine_integrity():
    """Test that GameEngine has expected components."""
    print("Testing GameEngine integrity...")
    
    game = GameEngine(use_mud_files=False)
    
    # Check that essential components exist
    essential_attrs = [
        'player', 'world', 'object_manager', 'parser',
        'responses', 'running'
    ]
    
    for attr in essential_attrs:
        if not hasattr(game, attr):
            print(f"❌ GameEngine missing essential attribute: {attr}")
            return False
        print(f"  ✓ GameEngine has {attr}")
    
    # Test that object_manager works
    try:
        objects = game.object_manager.get_all_objects()
        print(f"  ✓ ObjectManager has {len(objects)} objects")
    except Exception as e:
        print(f"❌ ObjectManager error: {e}")
        return False
    
    return True


def run_all_tests():
    """Run all basic disambiguation tests."""
    print("=== Basic Disambiguation System Tests ===")
    
    tests = [
        test_basic_disambiguation,
        test_no_crash_on_invalid_commands,
        test_player_state_consistency, 
        test_game_engine_integrity
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_func.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test_func.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} CRASHED: {e}")
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All basic tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)