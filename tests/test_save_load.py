#!/usr/bin/env python3
"""
Test script for the save/load system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import tempfile
import shutil
from pathlib import Path
from src.game import GameEngine

def test_save_load_system():
    """Test the save/load functionality"""
    print("Testing Save/Load System")
    print("=" * 40)
    
    # Create a temporary directory for test saves
    temp_dir = Path("test_saves")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Create game instance
        game = GameEngine(use_mud_files=False)
        
        print("\n1. Testing Game State Collection:")
        
        # Modify some game state
        game.player.move_to_room("NHOUS")
        game.player.add_to_inventory("BELL")
        game.player.add_to_inventory("KEYS") 
        game.score_manager.moves = 5
        game.score_manager.raw_score = 10
        
        # Test state collection
        original_state = game._collect_game_state()
        print(f"✓ Collected game state with {len(original_state)} top-level components")
        print(f"  - Player room: {original_state['player_state']['current_room']}")
        print(f"  - Player inventory: {original_state['player_state']['inventory']}")
        print(f"  - Score moves: {original_state['score_state']['moves']}")
        print(f"  - Raw score: {original_state['score_state']['raw_score']}")
        
        print("\n2. Testing Save Functionality:")
        
        # Test saving to custom filename
        test_save_file = "test_save.json"
        save_path = temp_dir / test_save_file
        
        # Temporarily change saves directory for testing
        original_saves_dir = "saves"
        # Create a custom save method for testing
        def test_save():
            game_state = game._collect_game_state()
            save_path.parent.mkdir(exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            return True
        
        success = test_save()
        
        if success and save_path.exists():
            print(f"✓ Save successful: {save_path}")
            
            # Verify save file content
            with open(save_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            print(f"✓ Save file contains {len(saved_data)} sections")
            print(f"  - Version: {saved_data.get('version', 'unknown')}")
            print(f"  - Has world state: {'world_state' in saved_data}")
            print(f"  - Has player state: {'player_state' in saved_data}")
        else:
            print("✗ Save failed")
            return
        
        print("\n3. Testing Load Functionality:")
        
        # Create a new game instance to load into
        new_game = GameEngine(use_mud_files=False)
        
        # Verify initial state is different
        print(f"New game initial room: {new_game.player.current_room}")
        print(f"New game initial inventory: {new_game.player.inventory}")
        
        # Load the saved state
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                saved_state = json.load(f)
            
            new_game._restore_game_state(saved_state)
            
            print("✓ Load successful")
            print(f"  - Loaded room: {new_game.player.current_room}")
            print(f"  - Loaded inventory: {new_game.player.inventory}")
            print(f"  - Loaded moves: {new_game.score_manager.moves}")
            print(f"  - Loaded score: {new_game.score_manager.raw_score}")
            
        except Exception as e:
            print(f"✗ Load failed: {e}")
            return
        
        print("\n4. Verifying State Restoration:")
        
        # Compare original and restored states
        success = True
        
        if new_game.player.current_room != original_state['player_state']['current_room']:
            print(f"✗ Room mismatch: {new_game.player.current_room} != {original_state['player_state']['current_room']}")
            success = False
        
        if new_game.player.inventory != original_state['player_state']['inventory']:
            print(f"✗ Inventory mismatch: {new_game.player.inventory} != {original_state['player_state']['inventory']}")
            success = False
        
        if new_game.score_manager.moves != original_state['score_state']['moves']:
            print(f"✗ Moves mismatch: {new_game.score_manager.moves} != {original_state['score_state']['moves']}")
            success = False
        
        if success:
            print("✓ All state successfully restored!")
        
        print("\n5. Testing Combination State Persistence:")
        
        # Test combination manager state
        if hasattr(new_game, 'combination_manager') and new_game.combination_manager:
            print("✓ Combination manager present after load")
            
            # Test if interaction state is preserved
            interactions = new_game.combination_manager.interaction_rules
            print(f"✓ {len(interactions)} interaction rules loaded")
            
        else:
            print("✗ Combination manager not found after load")
        
        print("\n6. Testing Object State Persistence:")
        
        # Perform an object transformation and verify it persists
        if "BELL" in new_game.player.inventory:
            print("✓ Bell found in inventory after load")
            
            # Try to heat the bell (if torch available or simulate)
            bell = new_game.objects.get("BELL")
            if bell:
                print(f"✓ Bell object available: {bell.name}")
            
        print("\nSave/Load system test complete!")
        
    finally:
        # Clean up test files
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"✓ Cleaned up test directory: {temp_dir}")

if __name__ == "__main__":
    test_save_load_system()