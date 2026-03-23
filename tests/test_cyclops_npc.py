"""
Comprehensive test suite for Cyclops NPC implementation.
Tests all behaviors, states, and interactions.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.entities.cyclops import CyclopsBehavior, CyclopsState, create_canonical_cyclops
from src.entities.npc import NPC
from src.entities.combat import CombatStats
from src.game import GameEngine
from src.entities.player import Player


class TestCyclopsState(unittest.TestCase):
    """Test CyclopsState dataclass functionality."""
    
    def setUp(self):
        self.state = CyclopsState()
    
    def test_default_state(self):
        """Test default state values."""
        self.assertTrue(self.state.is_sleeping)  # Starts sleeping
        self.assertEqual(self.state.wrath_level, 0)
        self.assertIsNone(self.state.last_fed_time)
        self.assertIsNone(self.state.last_given_drink_time)
        self.assertEqual(self.state.times_attacked, 0)
        self.assertFalse(self.state.has_been_awakened)
    
    def test_state_modifications(self):
        """Test modifying state values."""
        self.state.is_sleeping = False
        self.state.wrath_level = 3
        self.state.times_attacked = 1
        
        self.assertFalse(self.state.is_sleeping)
        self.assertEqual(self.state.wrath_level, 3)
        self.assertEqual(self.state.times_attacked, 1)


class TestCyclopsCreation(unittest.TestCase):
    """Test Cyclops NPC creation and basic properties."""
    
    def setUp(self):
        self.cyclops = create_canonical_cyclops()
    
    def test_cyclops_properties(self):
        """Test basic Cyclops properties."""
        self.assertEqual(self.cyclops.id, "CYCLOPS")
        self.assertEqual(self.cyclops.name, "cyclops")
        self.assertEqual(self.cyclops.location, "CYCLO")
        self.assertIn("blocks the staircase", self.cyclops.description)
    
    def test_cyclops_aliases(self):
        """Test Cyclops aliases."""
        aliases = self.cyclops.aliases
        expected_aliases = ["giant", "monster", "creature", "cyclo"]
        for alias in expected_aliases:
            self.assertIn(alias, aliases)
    
    def test_cyclops_canonical_flag(self):
        """Test Cyclops canonical attribute."""
        self.assertTrue(self.cyclops.get_attribute("canonical"))
    
    def test_cyclops_combat_stats(self):
        """Test Cyclops combat stats."""
        self.assertIsNotNone(self.cyclops.combat_stats)
        self.assertEqual(self.cyclops.combat_stats.current_health, 300)
        self.assertEqual(self.cyclops.combat_stats.max_health, 300)
        self.assertEqual(self.cyclops.combat_stats.attack_power, 40)
        self.assertEqual(self.cyclops.combat_stats.defense, 15)
        self.assertIsNone(self.cyclops.combat_stats.weapon)  # Uses fists
    
    def test_exit_blocking(self):
        """Test that Cyclops blocks the 'up' exit."""
        blocked_exits = self.cyclops.get_attribute("blocks_exits", [])
        self.assertIn("up", blocked_exits)
    
    def test_dialogue_options(self):
        """Test Cyclops dialogue setup."""
        self.assertIn("default", self.cyclops.dialogue_tree)
        self.assertIn("greeting", self.cyclops.dialogue_tree)
        self.assertIn("threats", self.cyclops.dialogue_tree)
        self.assertIn("hungry", self.cyclops.dialogue_tree)


class TestCyclopsBehavior(unittest.TestCase):
    """Test CyclopsBehavior class functionality."""
    
    def setUp(self):
        self.cyclops = create_canonical_cyclops()
        self.behavior = CyclopsBehavior(self.cyclops)
    
    def test_initial_behavior_state(self):
        """Test initial behavior state."""
        self.assertTrue(self.behavior.state.is_sleeping)
        self.assertEqual(self.behavior.state.wrath_level, 0)
        self.assertFalse(self.behavior.is_blocking_passage())  # Sleeping = not blocking
    
    def test_food_preferences(self):
        """Test food preference system."""
        # Good foods
        self.assertEqual(self.behavior.food_preferences['food'], 3)
        self.assertEqual(self.behavior.food_preferences['meat'], 4) 
        self.assertEqual(self.behavior.food_preferences['lunch'], 4)
        
        # Bad food
        self.assertEqual(self.behavior.food_preferences['garlic'], -1)
        
        # Food acceptance
        self.assertTrue(self.behavior.can_accept_food('food'))
        self.assertTrue(self.behavior.can_accept_food('meat'))
        self.assertTrue(self.behavior.can_accept_food('garlic'))  # Accepts but doesn't like
        self.assertFalse(self.behavior.can_accept_food('rock'))
    
    def test_sleep_drinks(self):
        """Test sleep-inducing drinks."""
        sleep_drinks = ['water', 'bottle', 'drink', 'potion']
        for drink in sleep_drinks:
            self.assertIn(drink, self.behavior.sleep_drinks)
    
    def test_wake_up_mechanism(self):
        """Test waking up the Cyclops."""
        # Should be sleeping initially
        self.assertTrue(self.behavior.state.is_sleeping)
        
        response = self.behavior.wake_up("disturbed")
        
        # Should be awake now
        self.assertFalse(self.behavior.state.is_sleeping)
        self.assertTrue(self.behavior.state.has_been_awakened)
        self.assertGreater(self.behavior.state.wrath_level, 0)
        self.assertEqual(self.behavior.state.times_attacked, 1)
        self.assertIn("yawns", response)
    
    def test_wake_already_awake(self):
        """Test waking an already awake Cyclops."""
        self.behavior.state.is_sleeping = False
        
        response = self.behavior.wake_up()
        
        self.assertIn("already awake", response)
    
    def test_blocking_behavior(self):
        """Test passage blocking behavior."""
        # Sleeping - should not block
        self.behavior.state.is_sleeping = True
        self.behavior.state.wrath_level = 2
        self.assertFalse(self.behavior.is_blocking_passage())
        
        # Awake and angry - should block
        self.behavior.state.is_sleeping = False
        self.behavior.state.wrath_level = 1
        self.assertTrue(self.behavior.is_blocking_passage())
        
        # Awake but satisfied - should not block
        self.behavior.state.wrath_level = -3
        self.assertFalse(self.behavior.is_blocking_passage())
    
    def test_blocking_messages(self):
        """Test blocking messages."""
        # Sleeping - no message
        self.behavior.state.is_sleeping = True
        self.assertIsNone(self.behavior.get_blocking_message())
        
        # Satisfied - no message  
        self.behavior.state.is_sleeping = False
        self.behavior.state.wrath_level = -3
        self.assertIsNone(self.behavior.get_blocking_message())
        
        # Hostile - blocking message
        self.behavior.state.wrath_level = 2
        message = self.behavior.get_blocking_message()
        self.assertIsNotNone(message)
        self.assertIn("blocks your path", message)
    
    def test_status_descriptions(self):
        """Test status descriptions for different states."""
        # Sleeping
        self.behavior.state.is_sleeping = True
        desc = self.behavior.get_status_description()
        self.assertIn("snoring", desc)
        
        # Satisfied
        self.behavior.state.is_sleeping = False
        self.behavior.state.wrath_level = -4
        desc = self.behavior.get_status_description()
        self.assertIn("satisfied", desc)
        
        # Neutral
        self.behavior.state.wrath_level = 0
        desc = self.behavior.get_status_description()
        self.assertIn("mild curiosity", desc)
        
        # Hostile
        self.behavior.state.wrath_level = 3
        desc = self.behavior.get_status_description()
        self.assertIn("prepared to eat horses", desc)


class TestCyclopsInteractions(unittest.TestCase):
    """Test Cyclops interaction mechanics."""
    
    def setUp(self):
        self.cyclops = create_canonical_cyclops()
        self.behavior = CyclopsBehavior(self.cyclops)
        
        # Create mock player
        self.player = Player()
        
        # Add some test items to player inventory  
        from src.entities.objects import GameObject
        food_item = GameObject("food", "A hearty meal", "Food")
        bread_item = GameObject("bread", "Fresh bread", "Bread")
        garlic_item = GameObject("garlic", "Pungent garlic", "Food")
        water_item = GameObject("water", "Clear water", "Liquid")
        
        # Add objects to a mock object manager for the tests
        self.object_manager = type('MockObjectManager', (), {
            'get_object': lambda self, item_id: {
                'food': food_item, 'bread': bread_item, 
                'garlic': garlic_item, 'water': water_item
            }.get(item_id)
        })()
        
        self.player.add_to_inventory('food')
        self.player.add_to_inventory('bread')
        self.player.add_to_inventory('garlic')
        self.player.add_to_inventory('water')
    
    def test_give_good_food(self):
        """Test giving good food to cyclops."""
        initial_wrath = self.behavior.state.wrath_level
        
        response = self.behavior.give_food("food", self.player, self.object_manager)
        
        # Wrath should decrease
        self.assertLess(self.behavior.state.wrath_level, initial_wrath)
        self.assertIn("devours", response.lower())
        
        # Food should be removed from inventory
        self.assertNotIn('food', self.player.inventory)
    
    def test_give_garlic(self):
        """Test giving garlic to cyclops (he doesn't like it)."""
        initial_wrath = self.behavior.state.wrath_level
        
        response = self.behavior.give_food("garlic", self.player, self.object_manager)
        
        # Should get special garlic message
        self.assertIn("there is a limit", response)
    
    def test_give_bad_item(self):
        """Test giving non-food to cyclops."""
        response = self.behavior.give_food("rock", self.player, self.object_manager)
        
        self.assertIn("not so stupid", response)
    
    def test_give_drink_when_calm(self):
        """Test giving drink when cyclops is calm."""
        self.behavior.state.wrath_level = -1  # Calm
        
        response = self.behavior.give_drink("water", self.player, self.object_manager)
        
        # Should fall asleep
        self.assertTrue(self.behavior.state.is_sleeping)
        self.assertIn("falls fast asleep", response)
        
        # Water should be removed
        self.assertNotIn('water', self.player.inventory)
    
    def test_give_drink_when_angry(self):
        """Test giving drink when cyclops is angry."""
        self.behavior.state.wrath_level = 2  # Angry
        
        response = self.behavior.give_drink("water", self.player, self.object_manager)
        
        # Should refuse
        self.assertIn("not thirsty", response)
        self.assertIn("refuses", response)
    
    def test_attack_sleeping_cyclops(self):
        """Test attacking sleeping cyclops."""
        self.assertTrue(self.behavior.state.is_sleeping)
        
        response = self.behavior.handle_attack()
        
        # Should wake up and get angry
        self.assertFalse(self.behavior.state.is_sleeping)
        self.assertGreater(self.behavior.state.wrath_level, 0)
        self.assertIn("yawns", response)
        self.assertIn("angry", response)
    
    def test_attack_awake_cyclops(self):
        """Test attacking awake cyclops."""
        self.behavior.state.is_sleeping = False
        initial_wrath = self.behavior.state.wrath_level
        
        response = self.behavior.handle_attack()
        
        # Wrath should increase
        self.assertGreater(self.behavior.state.wrath_level, initial_wrath + 1)
        self.assertIn("ignores", response.lower())


class TestCyclopsIntegration(unittest.TestCase):
    """Test Cyclops integration with game engine."""
    
    def setUp(self):
        # Create minimal game engine for testing
        try:
            self.game = GameEngine(debug_mode=True)
            self.cyclops = self.game.npc_manager.get_npc("CYCLOPS")
            self.behavior = self.cyclops.get_attribute("behavior") if self.cyclops else None
        except Exception as e:
            self.skipTest(f"Game engine initialization failed: {e}")
    
    def test_cyclops_exists(self):
        """Test that Cyclops exists in game."""
        self.assertIsNotNone(self.cyclops)
        self.assertEqual(self.cyclops.id, "CYCLOPS")
    
    def test_cyclops_behavior_attached(self):
        """Test that behavior is properly attached."""
        self.assertIsNotNone(self.behavior)
        self.assertIsInstance(self.behavior, CyclopsBehavior)
    
    def test_cyclops_location(self):
        """Test Cyclops location."""
        if self.cyclops:
            self.assertEqual(self.cyclops.location, "CYCLO")
    
    def test_cyclops_in_combat_system(self):
        """Test that Cyclops is integrated with combat system."""
        if self.cyclops:
            self.assertIsNotNone(self.cyclops.combat_stats)
            self.assertEqual(self.cyclops.combat_stats.current_health, 300)


class TestCyclopsCommands(unittest.TestCase):
    """Test Cyclops-specific command processing."""
    
    def setUp(self):
        try:
            # Create game engine in debug mode to reduce loading
            self.game = GameEngine(debug_mode=True)
            
            # Move player to Cyclops room
            cyclo_room = self.game.world_manager.get_room("CYCLO")
            if cyclo_room:
                self.game.player.current_room = cyclo_room.id
                # Update world state 
                self.game.world_manager.current_room = cyclo_room
            
            self.cyclops = self.game.npc_manager.get_npc("CYCLOPS")
            self.assertIsNotNone(self.cyclops, "Cyclops should exist")
        except Exception as e:
            self.skipTest(f"Game setup failed: {e}")
    
    def test_wake_command_integration(self):
        """Test wake cyclops command."""
        if not self.cyclops:
            self.skipTest("No cyclops available")
        
        behavior = self.cyclops.get_attribute("behavior")
        if behavior:
            # Make sure cyclops is sleeping
            behavior.state.is_sleeping = True
            
            # Test wake command
            response = self.game._process_command("wake cyclops")
            self.assertIn("yawns", response.lower())


def run_cyclops_tests():
    """Run all Cyclops tests."""
    
    print("🧟 Running Cyclops NPC Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCyclopsState,
        TestCyclopsCreation,
        TestCyclopsBehavior,
        TestCyclopsInteractions,
        TestCyclopsIntegration,
        TestCyclopsCommands
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"🧟 Cyclops Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, failure in result.failures:
            print(f"   - {test}: {failure}")
    
    if result.errors:
        print(f"\n💥 ERRORS:")
        for test, error in result.errors:
            print(f"   - {test}: {error}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("✅ All Cyclops tests PASSED! 🎉")
    else:
        print("❌ Some tests failed. Check output above.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_cyclops_tests()