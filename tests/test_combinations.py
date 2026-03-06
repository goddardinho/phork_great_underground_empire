#!/usr/bin/env python3
"""
Test script for the object combination system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from io import StringIO
from src.game import GameEngine
from src.parser.command_parser import Command
from src.combinations import InteractionType

def test_combination_system():
    """Test the object combination system with various interactions"""
    print("Testing Object Combination System")
    print("=" * 40)
    
    # Create game instance
    game = GameEngine(use_mud_files=False)  # Use simple test world
    
    print("\n1. Checking Combination Objects Registration:")
    combination_objects = ["BELL", "HBELL", "ROPE", "HOOK", "GRAPPLING_HOOK", 
                          "CROWBAR", "MIRROR", "BROKEN_MIRROR"]
    
    for obj_id in combination_objects:
        if obj_id in game.objects:
            obj = game.objects[obj_id]
            print(f"✓ {obj_id}: {obj.name}")
        else:
            print(f"✗ {obj_id}: NOT FOUND")
    
    print("\n2. Checking Object Placement in Rooms:")
    
    # Check north house for bell
    north_house = game.world.get_room("NHOUS")
    if north_house:
        print(f"North House items: {north_house.items}")
        if "BELL" in north_house.items:
            print("✓ Bell found in North House")
        else:
            print("✗ Bell not found in North House")
    
    # Check cave for rope  
    cave = game.world.get_room("CAVE")
    if cave:
        print(f"Cave items: {cave.items}")
        if "ROPE" in cave.items:
            print("✓ Rope found in Cave")
        else:
            print("✗ Rope not found in Cave")
    
    # Check temple for mirror
    temple = game.world.get_room("TEMPLE")
    if temple:
        print(f"Temple items: {temple.items}")
        if "MIRROR" in temple.items:
            print("✓ Mirror found in Temple")
        else:
            print("✗ Mirror not found in Temple")
    
    print("\n3. Testing Combination Manager:")
    if hasattr(game, 'combination_manager'):
        print("✓ Combination manager is initialized")
        
        # Test if some interactions are registered
        interactions = game.combination_manager.interaction_rules
        print(f"Total registered interactions: {len(interactions)}")
        
        # Check for specific interactions
        bell_interactions = [rule_id for rule_id, rule in interactions.items() 
                           if "BELL" in rule.primary_object or (rule.result_object and "HBELL" in rule.result_object)]
        print(f"Bell-related interactions: {len(bell_interactions)}")
        if bell_interactions:
            print(f"  Found: {bell_interactions}")
        
        rope_interactions = [rule_id for rule_id, rule in interactions.items() 
                           if "ROPE" in rule.primary_object and rule.secondary_object and "HOOK" in rule.secondary_object]
        print(f"Rope+Hook interactions: {len(rope_interactions)}")
        if rope_interactions:
            print(f"  Found: {rope_interactions}")
        
    else:
        print("✗ Combination manager not found")
    
    print("\n4. Testing Command Parser Integration:")
    # Test if combination commands are recognized
    parser = game.parser
    
    test_commands = [
        "heat bell",
        "cool bell", 
        "combine rope hook",
        "break mirror with crowbar",
        "pour water on fire",
        "use crowbar on door"
    ]
    
    for cmd_text in test_commands:
        try:
            command = parser.parse(cmd_text)
            print(f"✓ '{cmd_text}' -> {command.verb} command")
        except Exception as e:
            print(f"✗ '{cmd_text}' -> Error: {e}")
    
    print("\n5. Testing Simple Heat Interaction:")
    # Move player to north house and try to simulate heating bell
    game.player.move_to_room("NHOUS") 
    
    # Manually put bell in inventory for testing
    if "BELL" in game.objects:
        bell = game.objects["BELL"]
        game.player.add_to_inventory(bell.id)
        print("✓ Bell added to inventory for testing")
        
        # Test combination manager directly
        try:
            print("Attempting to heat the bell...")
            # Test if we can apply the heat interaction
            result = game.combination_manager.can_interact("BELL", "TORCH", "heat")
            
            if result:
                print(f"✓ Heat interaction is available: {result.id}")
                
                # Try to perform the interaction
                interaction_result = game.combination_manager.perform_interaction(
                    "BELL", "TORCH", "heat", game.player, game.objects
                )
                
                if interaction_result:
                    print(f"✓ Interaction performed successfully")
                else:
                    print("✗ Interaction failed")
            else:
                print("✗ Heat interaction not available")
                
            # Check current inventory
            print(f"Current inventory: {game.player.inventory}")
            
            # Try to get available interactions for the bell
            available = game.combination_manager.get_available_interactions("BELL")
            print(f"Available interactions for BELL: {[rule.id for rule in available]}")
            
        except Exception as e:
            print(f"✗ Error testing heat interaction: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nCombination system test complete!")

if __name__ == "__main__":
    test_combination_system()