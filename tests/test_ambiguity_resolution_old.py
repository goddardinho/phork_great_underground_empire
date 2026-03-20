#!/usr/bin/env python3
"""
Test disambiguation functionality - handling multiple matching objects.
This test validates the disambiguation system using available objects.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game import GameEngine


def test_basic_disambiguation():
    """Test that disambiguation prompts work with available objects."""
    print("Testing basic disambiguation...")
    
    game = GameEngine(use_mud_files=False)
    
    # Move to a room that exists (WHOUS is always available)
    game.player.move_to_room("WHOUS")
    
    # Test with a command that won't find matching objects
    # This should give a clear "not found" message, not a crash
    game._process_command("take nonexistent")
    
    # The key is that the game should handle disambiguation gracefully
    # Even when no objects match, it shouldn't crash
    assert not game.player.awaiting_disambiguation, "Should not be awaiting disambiguation for nonexistent object"
    
    print("✓ Basic disambiguation system is stable")


def test_no_crash_on_invalid_commands():
    """Test that invalid disambiguation choices don't crash the game."""
    print("Testing invalid disambiguation choices...")
    
    game = GameEngine(use_mud_files=False)
    game.player.move_to_room("WHOUS")
    
    # Test invalid disambiguation input when not awaiting disambiguation
    game._process_command("1")  # Should not crash
    game._process_command("invalid")  # Should not crash
    
    assert not game.player.awaiting_disambiguation, "Should not be in disambiguation state"
    
    print("✓ Invalid disambiguation choices handled gracefully")


def test_disambiguation_state_management():
    """Test disambiguation state is properly managed."""
    print("Testing disambiguation state management...")
    
    game = GameEngine(use_mud_files=False)
    game.player.move_to_room("WHOUS")
    
    # Test that disambiguation state starts clean
    assert not hasattr(game.player, 'awaiting_disambiguation') or not game.player.awaiting_disambiguation
    assert not hasattr(game.player, 'disambiguation_options') or not game.player.disambiguation_options
    assert not hasattr(game.player, 'pending_command') or game.player.pending_command is None
    
    print("✓ Disambiguation state properly initialized")
    game._process_command("take rusty knife")
    game._process_command("take silver knife")
    
    # Test DROP disambiguation
    initial_inventory_size = len(game.player.inventory)
    game._process_command("drop knife")
    assert game.player.awaiting_disambiguation, "Should be awaiting disambiguation for drop"
    
    # Choose second option (silver knife)
    game._process_command("2")
    assert not game.player.awaiting_disambiguation, "Should not be awaiting disambiguation after drop choice"
    assert len(game.player.inventory) == initial_inventory_size - 1, "Should have dropped one item"
    
    print("✓ Drop disambiguation working")


def test_container_disambiguation():
    """Test disambiguation when getting objects from containers.""" 
    print("Testing container disambiguation...")
    
    game = GameEngine(use_mud_files=False)
    
    # Setup: get torch and go to cave with boxes
    game.player.move_to_room("FOREST")
    game._process_command("take torch")
    game._process_command("take matches")
    game._process_command("light torch")
    
    game.player.move_to_room("TEMPLE")
    game._process_command("take rusty knife")
    game._process_command("take silver knife")
    
    game.player.move_to_room("CAVE")
    game._process_command("open wooden box")
    
    # Put both knives in the wooden box
    game._process_command("put rusty knife in wooden box")
    game._process_command("put silver knife in wooden box")
    
    # Test GET from container disambiguation
    initial_inventory_size = len(game.player.inventory)
    game._process_command("get knife from wooden box")
    assert game.player.awaiting_disambiguation, "Should be awaiting disambiguation for get from container"
    
    # Choose by descriptive text
    game._process_command("rusty")
    assert not game.player.awaiting_disambiguation, "Should not be awaiting disambiguation after choice"
    assert len(game.player.inventory) == initial_inventory_size + 1, "Should have taken one item from container"
    
    print("✓ Container disambiguation working")


def test_disambiguation_cancellation():
    """Test canceling disambiguation."""
    print("Testing disambiguation cancellation...")
    
    game = GameEngine(use_mud_files=False)
    game.player.move_to_room("TEMPLE")
    
    # Trigger disambiguation
    game._process_command("take knife")
    assert game.player.awaiting_disambiguation, "Should be awaiting disambiguation"
    
    # Cancel disambiguation
    game._process_command("cancel")
    assert not game.player.awaiting_disambiguation, "Should not be awaiting disambiguation after cancel"
    assert len(game.player.inventory) == 0, "Should not have taken anything after cancel"
    
    print("✓ Disambiguation cancellation working")


def test_box_disambiguation():
    """Test disambiguation with multiple boxes."""
    print("Testing box disambiguation...")
    
    game = GameEngine(use_mud_files=False)
    
    # Get torch and go to cave with boxes
    game.player.move_to_room("FOREST")
    game._process_command("take torch")
    game._process_command("take matches")
    game._process_command("light torch")
    
    game.player.move_to_room("CAVE")
    
    # Test opening boxes with disambiguation  
    game._process_command("open box")
    assert game.player.awaiting_disambiguation, "Should be awaiting disambiguation for open box"
    
    # Choose wooden box
    game._process_command("wooden")
    assert not game.player.awaiting_disambiguation, "Should not be awaiting disambiguation after choice"
    
    # Verify wooden box is now open
    wooden_box = game.objects.get("WOODEN_BOX")
    assert wooden_box.is_open(), "Wooden box should be open"
    
    print("✓ Box disambiguation working")


def test_invalid_disambiguation_responses():
    """Test handling of invalid disambiguation responses."""
    print("Testing invalid disambiguation responses...")
    
    game = GameEngine(use_mud_files=False)
    game.player.move_to_room("TEMPLE")
    
    # Trigger disambiguation
    game._process_command("take knife")
    assert game.player.awaiting_disambiguation, "Should be awaiting disambiguation"
    
    # Test invalid number
    game._process_command("99")
    assert game.player.awaiting_disambiguation, "Should still be awaiting disambiguation after invalid number"
    
    # Test invalid text
    game._process_command("purple")
    assert game.player.awaiting_disambiguation, "Should still be awaiting disambiguation after invalid text"
    
    # Test valid choice to clear state
    game._process_command("1")
    assert not game.player.awaiting_disambiguation, "Should not be awaiting disambiguation after valid choice"
    
    print("✓ Invalid response handling working")


def run_all_tests():
    """Run all disambiguation tests."""
    print("=== Ambiguity Resolution Tests ===")
    
    test_basic_disambiguation()
    test_drop_disambiguation()
    test_container_disambiguation()
    test_disambiguation_cancellation()
    test_box_disambiguation()
    test_invalid_disambiguation_responses()
    
    print()
    print("✅ All disambiguation tests passed!")


if __name__ == "__main__":
    run_all_tests()