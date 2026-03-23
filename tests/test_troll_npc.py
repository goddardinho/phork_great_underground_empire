"""Comprehensive test suite for Troll NPC functionality - Phase 3 Canonical NPCs"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from entities.troll import TrollBehavior, create_canonical_troll, integrate_troll_behaviors
from entities.npc import NPC
from entities.objects import GameObject
from entities.npc_manager import NPCManager
from entities.object_manager import ObjectManager
from entities.player import Player
from entities.combat import CombatStats
from game import GameEngine


class TestTrollBehavior(unittest.TestCase):
    """Test Troll behavior mechanics."""
    
    def setUp(self):
        """Set up test environment."""
        self.npc_manager = NPCManager()
        self.troll = create_canonical_troll(self.npc_manager, starting_room="MTROL")
        self.behavior = self.troll.troll_behavior
        self.object_manager = ObjectManager()
        
        # Create test objects
        self.food_item = GameObject(
            id="BREAD",
            name="bread",
            description="Fresh baked bread",
            attributes={"takeable": True}
        )
        
        self.treasure_item = GameObject(
            id="JEWEL",
            name="jewel",
            description="A precious jewel", 
            attributes={"takeable": True, "treasure_value": 5}
        )
        
        self.weapon_item = GameObject(
            id="SWORD",
            name="sword",
            description="A sharp sword",
            attributes={"takeable": True, "weapon": True}
        )
        
        self.junk_item = GameObject(
            id="STICK",
            name="stick", 
            description="A worthless stick",
            attributes={"takeable": True}
        )
        
        # Register objects
        self.object_manager.add_object(self.food_item)
        self.object_manager.add_object(self.treasure_item)
        self.object_manager.add_object(self.weapon_item)
        self.object_manager.add_object(self.junk_item)
    
    def test_troll_creation(self):
        """Test that troll is created correctly."""
        self.assertEqual(self.troll.id, "TROLL")
        self.assertEqual(self.troll.name, "troll")
        self.assertEqual(self.troll.location, "MTROL")
        self.assertTrue(self.troll.get_attribute("blocks_passages"))
        self.assertTrue(self.troll.get_attribute("accepts_payments"))
        self.assertTrue(self.troll.get_attribute("bridge_guardian"))
        
    def test_troll_combat_stats(self):
        """Test troll has proper combat stats."""
        stats = self.troll.combat_stats
        self.assertIsNotNone(stats)
        self.assertEqual(stats.max_health, 150)
        self.assertEqual(stats.current_health, 150)
        self.assertEqual(stats.attack_power, 25)
        self.assertGreater(stats.defense, 10)
        self.assertIsNotNone(stats.weapon)  # Should have axe equipped
        
    def test_troll_axe_weapon(self):
        """Test troll has properly equipped axe."""
        axe = self.troll.combat_stats.weapon
        self.assertIsNotNone(axe)
        self.assertEqual(axe.id, "TROLL_AXE")
        self.assertTrue(axe.get_attribute("weapon"))
        self.assertFalse(axe.get_attribute("takeable"))  # Can't be taken due to heat
        self.assertTrue(axe.get_attribute("hot"))
        
    def test_passage_blocking_when_alive(self):
        """Test troll blocks passages when healthy."""
        self.assertTrue(self.behavior.should_block_passage())
        
    def test_passage_blocking_when_dead(self):
        """Test troll doesn't block passages when unconscious/dead."""
        self.troll.combat_stats.current_health = 0
        self.assertFalse(self.behavior.should_block_passage())
        
    def test_passage_blocking_after_payment(self):
        """Test troll allows passage temporarily after payment."""
        # Initially blocks
        self.assertTrue(self.behavior.should_block_passage())
        
        # Accept payment
        self.behavior.accept_payment("BREAD")
        
        # Should temporarily allow passage
        self.assertFalse(self.behavior.should_block_passage())
        
    def test_payment_satisfaction_expires(self):
        """Test payment satisfaction expires after time."""
        # Accept payment
        self.behavior.accept_payment("BREAD")
        
        # Should be satisfied initially
        self.assertTrue(self.behavior.is_satisfied_with_payment())
        
        # Mock time passing
        with patch('time.time', return_value=time.time() + 400):  # 400 seconds later
            self.assertFalse(self.behavior.is_satisfied_with_payment())
    
    def test_payment_evaluation_food_high_priority(self):
        """Test food items get highest priority for payments."""
        priority = self.behavior.evaluate_payment_item("BREAD", self.object_manager)
        self.assertGreaterEqual(priority, 10)  # Food should get high priority
        
    def test_payment_evaluation_treasure_high_priority(self):
        """Test treasure items get high priority."""
        priority = self.behavior.evaluate_payment_item("JEWEL", self.object_manager)
        self.assertGreaterEqual(priority, 8)  # Treasure should get good priority
        
    def test_payment_evaluation_weapon_medium_priority(self):
        """Test weapon items get medium priority."""
        priority = self.behavior.evaluate_payment_item("SWORD", self.object_manager)
        self.assertGreaterEqual(priority, 6)  # Weapons should get decent priority
        
    def test_payment_evaluation_junk_low_priority(self):
        """Test junk items get low priority."""
        priority = self.behavior.evaluate_payment_item("STICK", self.object_manager)
        self.assertLessEqual(priority, 2)  # Junk should get low priority
        
    def test_payment_acceptance(self):
        """Test payment acceptance mechanics."""
        response = self.behavior.accept_payment("BREAD")
        
        self.assertIn("BREAD", self.behavior.accepted_payments)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 10)  # Should have meaningful response
        self.assertFalse(self.behavior.is_blocking_passage)
        
    def test_combat_victory_handling(self):
        """Test handling of troll defeat in combat."""
        response = self.behavior.handle_combat_victory()
        
        self.assertFalse(self.behavior.is_blocking_passage)
        self.assertIsInstance(response, str)
        self.assertIn("passage", response.lower())
        
    def test_combat_recovery_handling(self):
        """Test handling of troll recovery."""
        # First defeat the troll
        self.behavior.handle_combat_victory()
        
        # Then recover
        self.troll.combat_stats.current_health = 50  # Partial recovery
        response = self.behavior.handle_combat_recovery()
        
        self.assertTrue(self.behavior.is_blocking_passage)
        self.assertIsInstance(response, str)
        
    def test_blocking_message_when_active(self):
        """Test blocking message when troll is active."""
        message = self.behavior.get_blocking_message()
        self.assertIn("blocks", message.lower())
        self.assertIn("axe", message.lower())
        
    def test_blocking_message_when_unconscious(self):
        """Test blocking message when troll is unconscious."""
        self.troll.combat_stats.current_health = 0
        message = self.behavior.get_blocking_message()
        self.assertIn("unconscious", message.lower())
        self.assertIn("open", message.lower())


class TestTrollIntegration(unittest.TestCase):
    """Test Troll integration with game engine."""
    
    def setUp(self):
        """Set up test game environment."""
        self.game = GameEngine(debug_mode=True)
        self.game.player.current_room = "MTROL"  # Put player in troll room
        
    def test_troll_present_in_game(self):
        """Test troll is properly added to game."""
        troll = self.game.npc_manager.get_npc("TROLL")
        self.assertIsNotNone(troll)
        self.assertEqual(troll.location, "MTROL")
        
    def test_movement_blocked_by_troll(self):
        """Test movement is blocked when troll is active."""
        troll = self.game.npc_manager.get_npc("TROLL")
        self.assertIsNotNone(troll)
        
        # Mock the look_around method to avoid room description issues
        with patch.object(self.game, '_look_around'):
            # Try to move - should be blocked
            original_room = self.game.player.current_room
            self.game._handle_movement("north")
            
            # Should still be in same room (movement blocked)
            self.assertEqual(self.game.player.current_room, original_room)
    
    def test_movement_allowed_when_troll_defeated(self):
        """Test movement is allowed when troll is defeated."""
        troll = self.game.npc_manager.get_npc("TROLL")
        
        # Defeat the troll
        troll.combat_stats.current_health = 0
        
        # Movement should now be allowed (if valid exits exist)
        with patch.object(self.game, '_look_around'):
            # This would normally move if exits exist - we're testing the troll doesn't block
            self.assertFalse(troll.troll_behavior.should_block_passage())


class TestTrollCombat(unittest.TestCase):
    """Test Troll combat interactions."""
    
    def setUp(self):
        """Set up combat test environment."""
        self.npc_manager = NPCManager()
        self.troll = create_canonical_troll(self.npc_manager)
        
    def test_troll_combat_readiness(self):
        """Test troll is ready for combat."""
        self.assertIsNotNone(self.troll.combat_stats)
        self.assertTrue(self.troll.combat_stats.is_alive())
        self.assertGreater(self.troll.combat_stats.attack_power, 20)
        
    def test_axe_damage_bonus(self):
        """Test troll's axe provides damage bonus."""
        base_damage = self.troll.combat_stats.attack_power
        total_damage = self.troll.combat_stats.get_attack_damage()
        
        # Should get bonus from axe (though there's randomness)
        axe_damage = self.troll.combat_stats.weapon.get_attribute("damage", 0)
        self.assertGreater(axe_damage, 0)
        
    def test_troll_is_hostile(self):
        """Test troll is marked as hostile."""
        self.assertTrue(self.troll.get_attribute("hostile"))


class TestTrollDialogue(unittest.TestCase):
    """Test Troll dialogue system."""
    
    def setUp(self):
        """Set up dialogue test environment."""
        self.npc_manager = NPCManager()
        self.troll = create_canonical_troll(self.npc_manager)
        
    def test_troll_has_dialogue_tree(self):
        """Test troll has proper dialogue tree."""
        self.assertIsNotNone(self.troll.dialogue_tree)
        self.assertIn("encounter", self.troll.dialogue_tree)
        self.assertIn("combat_challenge", self.troll.dialogue_tree)
        self.assertIn("negotiation", self.troll.dialogue_tree)
        
    def test_encounter_node_responses(self):
        """Test encounter node has proper responses."""
        encounter = self.troll.dialogue_tree["encounter"]
        self.assertGreaterEqual(len(encounter.responses), 3)
        
        # Should have fight, negotiate, and retreat options
        response_ids = [r.id for r in encounter.responses]
        self.assertIn("resp_fight", response_ids)
        self.assertIn("resp_negotiate", response_ids)
        self.assertIn("resp_retreat", response_ids)
        
    def test_combat_challenge_ends_conversation(self):
        """Test combat challenge node ends conversation."""
        combat_node = self.troll.dialogue_tree["combat_challenge"] 
        self.assertTrue(combat_node.end_conversation)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestTrollBehavior))
    suite.addTest(unittest.makeSuite(TestTrollIntegration))
    suite.addTest(unittest.makeSuite(TestTrollCombat))
    suite.addTest(unittest.makeSuite(TestTrollDialogue))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TROLL NPC TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")  
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
            
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Error:')[-1].strip()}")
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)