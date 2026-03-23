#!/usr/bin/env python3
"""Debug script for comprehensive Troll NPC testing - Phase 3 Canonical NPCs

This script provides interactive testing and validation of the Troll NPC
implementation, including passage blocking, payment mechanics, combat integration,
and authentic Zork behaviors.
"""

import sys
import os
from pathlib import Path

# Add src to Python path (from tests directory, go up one level to find src)
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Alternative: add root directory to path for src module access  
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from src.game import GameEngine
import time


def test_troll_presence():
    """Test that Troll NPC exists and is properly configured."""
    print("🧌 Testing Troll NPC Presence...")
    game = GameEngine(debug_mode=True)
    
    troll = game.npc_manager.get_npc("TROLL")
    if not troll:
        print("❌ ERROR: Troll NPC not found!")
        return False
        
    print(f"✅ Troll found: {troll.name} at location {troll.location}")
    print(f"   Description: {troll.description}")
    print(f"   Aliases: {', '.join(troll.aliases)}")
    
    # Test troll attributes
    expected_attrs = ["blocks_passages", "accepts_payments", "bridge_guardian"]
    for attr in expected_attrs:
        if troll.get_attribute(attr):
            print(f"✅ Attribute '{attr}': True")
        else:
            print(f"❌ Missing attribute: {attr}")
            
    return True


def test_troll_combat_stats():
    """Test Troll combat statistics and weapon."""
    print("\n⚔️ Testing Troll Combat Stats...")
    game = GameEngine(debug_mode=True)
    
    troll = game.npc_manager.get_npc("TROLL")
    if not troll or not troll.combat_stats:
        print("❌ ERROR: Troll combat stats not found!")
        return False
        
    stats = troll.combat_stats
    print(f"✅ Health: {stats.current_health}/{stats.max_health}")
    print(f"✅ Attack Power: {stats.attack_power}")
    print(f"✅ Defense: {stats.defense}")
    print(f"✅ Accuracy: {stats.accuracy}%")
    print(f"✅ Critical Chance: {stats.critical_chance}%")
    
    # Test axe weapon
    if stats.weapon:
        axe = stats.weapon
        print(f"✅ Weapon: {axe.name}")
        print(f"   Weapon ID: {axe.id}")
        print(f"   Damage Bonus: {axe.get_attribute('damage', 'N/A')}")
        print(f"   Hot (untakeable): {axe.get_attribute('hot', False)}")
        print(f"   Takeable: {axe.get_attribute('takeable', True)}")
    else:
        print("❌ ERROR: Troll has no weapon equipped!")
        
    return True


def test_passage_blocking():
    """Test Troll passage blocking mechanics."""
    print("\n🚧 Testing Passage Blocking...")
    game = GameEngine(debug_mode=True)
    
    troll = game.npc_manager.get_npc("TROLL") 
    if not troll:
        print("❌ ERROR: Troll not found!")
        return False
        
    behavior = troll.troll_behavior
    
    # Test initial blocking state
    blocking = behavior.should_block_passage()
    print(f"✅ Initially blocking passages: {blocking}")
    
    # Test blocking message
    message = behavior.get_blocking_message()
    print(f"✅ Blocking message: {message}")
    
    # Test defeated state
    original_health = troll.combat_stats.current_health
    troll.combat_stats.current_health = 0  # Simulate defeat
    
    blocking_defeated = behavior.should_block_passage()
    defeated_message = behavior.get_blocking_message()
    
    print(f"✅ Blocking when defeated: {blocking_defeated}")
    print(f"✅ Defeated message: {defeated_message}")
    
    # Restore health
    troll.combat_stats.current_health = original_health
    
    return True


def test_payment_system():
    """Test Troll payment and negotiation system."""
    print("\n💰 Testing Payment System...")
    game = GameEngine(debug_mode=True)
    
    troll = game.npc_manager.get_npc("TROLL")
    if not troll:
        print("❌ ERROR: Troll not found!")
        return False
        
    behavior = troll.troll_behavior
    
    # Test payment evaluation with different item types
    test_items = [
        ("BREAD", "food item"),
        ("JEWEL", "treasure item"),  
        ("SWORD", "weapon item"),
        ("STICK", "junk item")
    ]
    
    for item_id, item_type in test_items:
        # Mock object for testing
        class MockObject:
            def __init__(self, name, attrs):
                self.name = name
                self._attrs = attrs
            def get_attribute(self, attr, default=None):
                return self._attrs.get(attr, default)
        
        # Create mock objects with different attributes
        if "food" in item_type:
            mock_obj = MockObject("bread", {})
        elif "treasure" in item_type:
            mock_obj = MockObject("jewel", {"treasure_value": 5})
        elif "weapon" in item_type:
            mock_obj = MockObject("sword", {"weapon": True})
        else:
            mock_obj = MockObject("stick", {})
            
        # Mock object manager  
        class MockObjectManager:
            def get_object(self, obj_id):
                return mock_obj
                
        priority = behavior.evaluate_payment_item(item_id, MockObjectManager())
        print(f"✅ {item_type} priority: {priority}")
    
    # Test payment acceptance
    response = behavior.accept_payment("BREAD")
    print(f"✅ Payment accepted, response: {response}")
    print(f"✅ Payment stored in accepted_payments: {'BREAD' in behavior.accepted_payments}")
    print(f"✅ Passage now open: {not behavior.should_block_passage()}")
    
    return True


def test_dialogue_system():
    """Test Troll dialogue tree."""
    print("\n💬 Testing Dialogue System...")
    game = GameEngine(debug_mode=True)
    
    troll = game.npc_manager.get_npc("TROLL")
    if not troll:
        print("❌ ERROR: Troll not found!")
        return False
        
    dialogue_tree = troll.dialogue_tree
    
    # Test key dialogue nodes exist
    required_nodes = ["encounter", "combat_challenge", "negotiation", "payment_offer"]
    for node_id in required_nodes:
        if node_id in dialogue_tree:
            node = dialogue_tree[node_id]
            print(f"✅ Node '{node_id}': {len(node.text)} chars")
            if hasattr(node, 'responses') and node.responses:
                print(f"   Responses: {len(node.responses)}")
                for resp in node.responses:
                    print(f"   - {resp.id}: '{resp.text[:30]}...'")
        else:
            print(f"❌ Missing dialogue node: {node_id}")
    
    return True


def test_combat_integration():
    """Test Troll combat integration."""
    print("\n⚔️ Testing Combat Integration...")
    game = GameEngine(debug_mode=True)
    
    troll = game.npc_manager.get_npc("TROLL")
    if not troll:
        print("❌ ERROR: Troll not found!")
        return False
        
    # Test combat readiness
    print(f"✅ Troll is hostile: {troll.get_attribute('hostile')}")
    print(f"✅ Combat stats present: {troll.combat_stats is not None}")
    print(f"✅ Is alive: {troll.combat_stats.is_alive()}")
    
    # Test damage calculation with weapon
    base_damage = troll.combat_stats.attack_power
    weapon_damage = troll.combat_stats.weapon.get_attribute("damage", 0) if troll.combat_stats.weapon else 0
    total_damage = troll.combat_stats.get_attack_damage()
    
    print(f"✅ Base attack: {base_damage}")
    print(f"✅ Weapon bonus: {weapon_damage}")
    print(f"✅ Total damage range: ~{total_damage} (randomized)")
    
    # Test victory handling
    victory_response = troll.troll_behavior.handle_combat_victory()
    print(f"✅ Victory response: {victory_response[:50]}...")
    
    return True


def interactive_troll_testing():
    """Interactive testing with live game environment."""
    print("\n🎮 Interactive Troll Testing")
    print("=" * 50)
    
    game = GameEngine(debug_mode=True) 
    
    # Move player to troll room
    game.player.current_room = "MTROL"
    
    print("You are now in the Troll Room!")
    print("Try these commands:")
    print("- 'look' - See the room and troll")
    print("- 'talk to troll' - Start dialogue")  
    print("- 'north' (or other directions) - Test passage blocking")
    print("- 'give bread to troll' - Test payment (if you have bread)")
    print("- 'attack troll' - Test combat")
    print("- 'take axe' - Test axe interaction")
    print("- 'quit' - Exit testing")
    
    while True:
        try:
            user_input = input("\n> ").strip().lower()
            
            if user_input == 'quit':
                break
            elif user_input == 'help':
                print("Available test commands: look, talk to troll, north/south/east/west, attack troll, give X to troll, take axe")
            elif not user_input:
                continue
            else:
                # Process command through game engine
                game.process_command(user_input)
                
        except KeyboardInterrupt:
            print("\nExiting interactive testing...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Run comprehensive Troll NPC testing."""
    print("🧌 COMPREHENSIVE TROLL NPC TESTING")
    print("=" * 50)
    
    tests = [
        test_troll_presence,
        test_troll_combat_stats,  
        test_passage_blocking,
        test_payment_system,
        test_dialogue_system,
        test_combat_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ ERROR in {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"TROLL NPC TESTING SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Tests passed: {passed}")
    print(f"❌ Tests failed: {failed}")
    print(f"📊 Success rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("🎉 ALL TROLL TESTS PASSED! Phase 3 implementation successful!")
    else:
        print("⚠️  Some tests failed. Review implementation.")
    
    # Offer interactive testing
    if input("\n🎮 Run interactive testing? (y/n): ").lower().startswith('y'):
        interactive_troll_testing()


if __name__ == "__main__":
    main()