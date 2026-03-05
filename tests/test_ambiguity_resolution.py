#!/usr/bin/env python3
"""
Test disambiguation functionality - handling multiple matching objects.
Tests the "which sword - the rusty one or the silver one?" feature.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game import GameEngine


def test_basic_disambiguation():
    """Test basic object disambiguation with take/examine commands."""
    print("Testing basic disambiguation...")
    
    game = GameEngine(use_mud_files=False)
    game.player.move_to_room("TEMPLE")
    
    # Test TAKE disambiguation - should show options for multiple knives
    initial_inventory_size = len(game.player.inventory)
    
    # Process "take knife" - should trigger disambiguation
    game._process_command("take knife")
    assert game.player.awaiting_disambiguation, "Should be awaiting disambiguation"
    assert len(game.player.disambiguation_options) == 2, "Should have 2 knife options"
    assert game.player.pending_command is not None, "Should have pending command"
    
    # Choose first option (rusty knife)
    game._process_command("1")
    assert not game.player.awaiting_disambiguation, "Should not be awaiting disambiguation after choice"
    assert len(game.player.inventory) == initial_inventory_size + 1, "Should have taken one item"
    
    # Verify we took the rusty knife
    rusty_knife_in_inventory = any(
        game.objects.get(item_id).id == "RUSTY_KNIFE" 
        for item_id in game.player.inventory
    )
    assert rusty_knife_in_inventory, "Should have taken rusty knife"
    
    # Test EXAMINE disambiguation
    game._process_command("examine knife")
    assert game.player.awaiting_disambiguation, "Should be awaiting disambiguation for examine"
    
    # Choose by descriptive text (silver)  
    game._process_command("silver")
    assert not game.player.awaiting_disambiguation, "Should not be awaiting disambiguation after choice"
    
    print("✓ Basic disambiguation working")


def test_drop_disambiguation():
    """Test disambiguation when dropping objects from inventory."""
    print("Testing drop disambiguation...")
    
    game = GameEngine(use_mud_files=False)
    game.player.move_to_room("TEMPLE")
    
    # Take both knives
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