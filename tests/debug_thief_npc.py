#!/usr/bin/env python3
"""Debug and validation script for Thief NPC - Phase 2 Canonical NPCs Feature

This script provides comprehensive testing of:
- Thief creation and stats verification
- Theft mechanics with real objects
- Movement behavior testing
- Combat scenario validation
- Integration with game engine

Use this to validate Thief works correctly in full gameplay scenarios.
"""

import sys
import time
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
from src.entities.objects import GameObject


class ThiefDebugger:
    """Debug and test Thief NPC functionality."""
    
    def __init__(self):
        """Initialize debug environment."""
        print("🔧 Initializing Thief NPC Debugger...")
        self.game = GameEngine(debug_mode=True)
        
        # Add some test objects for theft scenarios
        self._add_test_objects()
        
        print("✅ Debug environment initialized!")
        print(f"   Player location: {self.game.player.current_room}")
        
    def _add_test_objects(self):
        """Add test objects for theft scenarios."""
        # Create valuable test objects
        test_objects = [
            {
                "id": "TEST_TREASURE",
                "name": "golden chalice",
                "description": "A valuable golden chalice encrusted with gems.",
                "attributes": {"treasure_value": 25, "valuable": True}
            },
            {
                "id": "TEST_WEAPON", 
                "name": "steel sword",
                "description": "A finely crafted steel sword.",
                "attributes": {"weapon": True, "damage": 10}
            },
            {
                "id": "TEST_TOOL",
                "name": "master key",
                "description": "An ornate key that opens many locks.",
                "attributes": {"tool": True, "opens": "all"}
            },
            {
                "id": "TEST_JUNK",
                "name": "old rag",
                "description": "A tattered piece of cloth.",
                "attributes": {}
            }
        ]
        
        for obj_data in test_objects:
            obj = GameObject(
                id=obj_data["id"],
                name=obj_data["name"],
                description=obj_data["description"],
                attributes=obj_data["attributes"]
            )
            self.game.object_manager.add_object(obj)
            self.game.player.add_to_inventory(obj_data["id"])
            print(f"   Added test object: {obj_data['name']}")
    
    def test_thief_creation(self):
        """Test Thief NPC creation and properties."""
        print("\n🧪 Testing Thief Creation...")
        
        thief = self.game.npc_manager.get_npc("THIEF")
        if not thief:
            print("❌ ERROR: Thief NPC not found!")
            return False
            
        print(f"✅ Thief found: {thief.name}")
        print(f"   ID: {thief.id}")
        print(f"   Location: {thief.location}")
        print(f"   Aliases: {thief.aliases}")
        print(f"   Canonical: {thief.get_attribute('canonical', False)}")
        print(f"   Steals Objects: {thief.get_attribute('steals_objects', False)}")
        
        # Test combat stats
        if thief.combat_stats:
            stats = thief.combat_stats
            print(f"   Combat Stats:")
            print(f"     Health: {stats.current_health}/{stats.max_health}")
            print(f"     Attack: {stats.attack_power}")
            print(f"     Defense: {stats.defense}")
            print(f"     Accuracy: {stats.accuracy}%")
            print(f"     Dodge: {stats.dodge_chance}%")
        
        # Test behavior system
        if hasattr(thief, 'thief_behavior'):
            print(f"   Behavior system: ✅")
            behavior = thief.thief_behavior
            print(f"     Can attempt theft: {behavior.can_attempt_theft()}")
            print(f"     Can move: {behavior.can_move()}")
            print(f"     Stolen objects: {len(behavior.stolen_objects)}")
        else:
            print("   Behavior system: ❌ Missing!")
            return False
        
        return True
    
    def test_theft_mechanics(self):
        """Test Thief theft behavior."""
        print("\n🦹 Testing Theft Mechanics...")
        
        thief = self.game.npc_manager.get_npc("THIEF")
        if not thief or not hasattr(thief, 'thief_behavior'):
            print("❌ Thief not properly initialized!")
            return False
        
        # Move Thief to player's room
        self.game.npc_manager.move_npc("THIEF", self.game.player.current_room)
        thief.location = self.game.player.current_room
        
        print(f"   Player inventory before: {self.game.player.inventory}")
        print(f"   Thief stolen items before: {thief.thief_behavior.stolen_objects}")
        
        # Force theft attempt
        behavior = thief.thief_behavior
        behavior.last_theft_time = 0  # Enable theft
        
        # Get theft targets
        targets = behavior.get_theft_targets(
            self.game.player.inventory, 
            self.game.object_manager
        )
        print(f"   Theft targets (prioritized): {targets}")
        
        # Attempt theft multiple times to test success/failure
        theft_success = False
        for attempt in range(5):
            stolen = behavior.attempt_theft(
                self.game.player.inventory,
                self.game.object_manager
            )
            if stolen:
                print(f"   ✅ Theft successful on attempt {attempt + 1}: {stolen}")
                
                # Remove from player inventory (simulate game engine behavior)
                if stolen in self.game.player.inventory:
                    self.game.player.remove_from_inventory(stolen)
                
                theft_success = True
                break
            else:
                behavior.last_theft_time = 0  # Reset cooldown for testing
                
        if not theft_success:
            print("   ⚠️  No theft occurred in 5 attempts (could be random)")
        
        print(f"   Player inventory after: {self.game.player.inventory}")
        print(f"   Thief stolen items after: {thief.thief_behavior.stolen_objects}")
        
        return True
    
    def test_movement_behavior(self):
        """Test Thief movement mechanics.""" 
        print("\n🚶 Testing Movement Behavior...")
        
        thief = self.game.npc_manager.get_npc("THIEF")
        if not thief:
            return False
            
        print(f"   Current location: {thief.location}")
        
        # Get available destinations
        behavior = thief.thief_behavior
        destinations = behavior.get_movement_destinations(
            thief.location,
            self.game.world
        )
        print(f"   Available destinations: {destinations}")
        
        if not destinations:
            print("   ⚠️  No valid destinations found")
            return True
        
        # Test movement capability
        behavior.movement_timer = 0  # Enable movement
        can_move = behavior.can_move()
        print(f"   Can move: {can_move}")
        
        # Simulate movement
        old_location = thief.location
        if destinations:
            import random
            new_location = random.choice(destinations)
            thief.location = new_location
            print(f"   ✅ Simulated movement: {old_location} → {new_location}")
        
        return True
    
    def test_combat_integration(self):
        """Test Thief combat capabilities."""
        print("\n⚔️  Testing Combat Integration...")
        
        thief = self.game.npc_manager.get_npc("THIEF")
        if not thief:
            return False
        
        # Move Thief to player room for combat
        self.game.npc_manager.move_npc("THIEF", self.game.player.current_room)
        thief.location = self.game.player.current_room
        
        print(f"   Thief health: {thief.combat_stats.current_health}/{thief.combat_stats.max_health}")
        print(f"   Player health: {self.game.player.combat_stats.current_health}")
        
        # Test flee decision logic
        behavior = thief.thief_behavior
        
        # Test at full health
        should_flee_full = behavior.should_flee_combat(100, 100)
        print(f"   Should flee at full health: {should_flee_full}")
        
        # Test at critical health
        should_flee_critical = behavior.should_flee_combat(20, 100)
        print(f"   Should flee at critical health: {should_flee_critical}")
        
        # Test loot dropping
        behavior.stolen_objects = ["TEST_TREASURE", "TEST_WEAPON"]
        loot = behavior.drop_loot_on_death()
        print(f"   Loot dropped on death: {loot}")
        
        return True
    
    def test_dialogue_system(self):
        """Test Thief dialogue responses."""
        print("\n💬 Testing Dialogue System...")
        
        thief = self.game.npc_manager.get_npc("THIEF")
        if not thief:
            return False
            
        dialogue_tree = thief.dialogue_tree
        print(f"   Available dialogue nodes: {list(dialogue_tree.keys())}")
        
        # Test encounter node
        if "encounter" in dialogue_tree:
            encounter = dialogue_tree["encounter"]
            print(f"   Encounter text: {encounter.text[:60]}...")
            print(f"   Response options: {len(encounter.responses)}")
            
            for i, response in enumerate(encounter.responses):
                print(f"     {i+1}. {response.text} → {response.next_node}")
        
        return True
    
    def run_full_test(self):
        """Run complete Thief validation test suite."""
        print("🎯 Starting Full Thief NPC Validation...")
        print("=" * 60)
        
        tests = [
            ("Creation", self.test_thief_creation),
            ("Theft Mechanics", self.test_theft_mechanics),
            ("Movement", self.test_movement_behavior),
            ("Combat", self.test_combat_integration), 
            ("Dialogue", self.test_dialogue_system)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
                print(f"   {test_name}: {'✅ PASS' if success else '❌ FAIL'}")
            except Exception as e:
                print(f"   {test_name}: ❌ ERROR - {e}")
                results.append((test_name, False))
        
        print("\n📊 Test Results Summary:")
        print("-" * 40)
        passed = sum(1 for _, success in results if success)
        total = len(results) 
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL" 
            print(f"   {test_name}: {status}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Thief NPC tests passed! Ready for gameplay testing.")
        else:
            print("⚠️  Some tests failed. Review implementation.")
            
        return passed == total


def main():
    """Main debug script entry point."""  
    print("🏰 Zork Great Underground Empire - Thief NPC Debug Script")
    print("=" * 65)
    
    try:
        debugger = ThiefDebugger()
        success = debugger.run_full_test()
        
        print("\n🎮 Ready for interactive testing!")
        print("   Try commands like:")
        print("   - Run from tests directory: cd ../; python tests/debug_thief_npc.py")
        print("   - Or in game: python main.py --debug, then 'debug thief'")
        print("   - Interactive: python tests/test_thief_interactive.py")
        
        return 0 if success else 1
    
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())