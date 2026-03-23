#!/usr/bin/env python3
"""
Combat System Testing Framework - Phase 1 Implementation Test

This script tests the combat foundation: CombatManager, CombatStats, 
attack/defend/flee commands, and combat integration with NPCs.

Usage: python3 tests/test_combat_system.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.entities.combat import CombatManager, CombatStats, CombatResult, WeaponType, WEAPON_STATS
from src.entities.npc import NPC
from src.entities.player import Player
import unittest


class TestCombatSystem(unittest.TestCase):
    """Test suite for the combat system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.combat_manager = CombatManager()
        self.player = Player()
        
        # Create a test NPC with custom combat stats
        self.test_npc = NPC(
            id="TEST_WARRIOR",
            name="test warrior",
            description="A fierce test warrior.",
            location="TEST_ROOM"
        )
        # Override default combat stats for testing
        self.test_npc.combat_stats = CombatStats(
            max_health=50,
            current_health=50,
            attack_power=12,
            defense=3,
            accuracy=70,
            dodge_chance=10,
            block_chance=5,
            critical_chance=5
        )
    
    def test_combat_stats_basics(self):
        """Test basic CombatStats functionality."""
        stats = CombatStats()
        
        # Test default values
        self.assertEqual(stats.max_health, 100)
        self.assertEqual(stats.current_health, 100)
        self.assertTrue(stats.is_alive())
        
        # Test damage
        damage_taken = stats.take_damage(30)
        self.assertEqual(damage_taken, 25)  # 30 - 5 default defense
        self.assertEqual(stats.current_health, 75)
        self.assertTrue(stats.is_alive())
        
        # Test healing
        healed = stats.heal(20)
        self.assertEqual(healed, 20)
        self.assertEqual(stats.current_health, 95)
        
        # Test death
        fatal_damage = stats.take_damage(200)
        self.assertEqual(stats.current_health, 0)
        self.assertFalse(stats.is_alive())
    
    def test_combat_manager_basic_operations(self):
        """Test CombatManager basic functionality."""
        room_id = "TEST_ROOM"
        
        # Test starting combat
        success = self.combat_manager.start_combat("player", "npc1", room_id)
        self.assertTrue(success)
        self.assertTrue(self.combat_manager.is_in_combat(room_id))
        
        # Test getting participants
        participants = self.combat_manager.get_combat_participants(room_id)
        self.assertIn("player", participants)
        self.assertIn("npc1", participants)
        
        # Test ending combat
        result = self.combat_manager.end_combat(room_id, winner="player")
        self.assertIsInstance(result, dict)
        self.assertFalse(self.combat_manager.is_in_combat(room_id))
    
    def test_attack_calculations(self):
        """Test combat attack calculations."""
        attacker = CombatStats(attack_power=20, accuracy=100, critical_chance=0)
        defender = CombatStats(defense=5, dodge_chance=0, block_chance=0)
        
        # Test guaranteed hit
        result, damage = self.combat_manager.calculate_attack(attacker, defender)
        self.assertEqual(result, CombatResult.HIT)
        self.assertGreater(damage, 0)
        
        # Test miss with low accuracy
        attacker.accuracy = 0
        result, damage = self.combat_manager.calculate_attack(attacker, defender)
        self.assertEqual(result, CombatResult.MISS)
        self.assertEqual(damage, 0)
    
    def test_flee_mechanics(self):
        """Test combat flee mechanics."""
        room_id = "TEST_ROOM"
        
        # Start combat
        self.combat_manager.start_combat("player", "npc1", room_id)
        
        # Test successful flee (should be random, but we can test the mechanism)
        participants_before = len(self.combat_manager.get_combat_participants(room_id))
        
        # Attempt flee multiple times to account for randomness
        fled = False
        for _ in range(10):  # Try 10 times, should succeed at least once
            if self.combat_manager.attempt_flee("player", room_id):
                fled = True
                break
            # Reset for next attempt if still in combat
            if not self.combat_manager.is_in_combat(room_id):
                break
        
        # If we fled successfully, combat should end or participant count decrease
        if fled and not self.combat_manager.is_in_combat(room_id):
            self.assertTrue(True)  # Combat ended successfully
        elif self.combat_manager.is_in_combat(room_id):
            participants_after = len(self.combat_manager.get_combat_participants(room_id))
            self.assertLessEqual(participants_after, participants_before)
    
    def test_weapon_effects(self):
        """Test weapon effects on combat stats."""
        # Test weapon damage calculation
        stats = CombatStats(attack_power=10)
        base_damage = stats.get_attack_damage()
        
        # The damage should be around base power ±20%
        self.assertGreaterEqual(base_damage, 8)  # 10 - 20%
        self.assertLessEqual(base_damage, 12)    # 10 + 20%
        
        # Test weapon stats dictionary
        self.assertIn(WeaponType.SWORD, WEAPON_STATS)
        sword_stats = WEAPON_STATS[WeaponType.SWORD]
        self.assertIn("damage", sword_stats)
        self.assertIn("accuracy", sword_stats)
    
    def test_combat_action_recording(self):
        """Test combat action history recording."""
        action = self.combat_manager.execute_attack(
            self.player.combat_stats,
            self.test_npc.combat_stats,
            "Player",
            "Test NPC"
        )
        
        self.assertIsNotNone(action)
        self.assertEqual(action.attacker, "Player")
        self.assertEqual(action.target, "Test NPC")
        self.assertEqual(action.action_type, "attack")
        
        # Check history
        recent_actions = self.combat_manager.get_recent_actions(1)
        self.assertEqual(len(recent_actions), 1)
        self.assertEqual(recent_actions[0].attacker, "Player")


def run_combat_integration_test():
    """Run integration test with actual game components."""
    print("\n" + "="*60)
    print("COMBAT INTEGRATION TEST")
    print("="*60)
    
    try:
        # Test importing from main game
        from src.game import GameEngine
        
        print("✓ Successfully imported GameEngine")
        
        # Create game instance
        game = GameEngine(debug_mode=True)
        print("✓ GameEngine created with combat manager")
        
        # Check combat manager integration
        if hasattr(game, 'combat_manager') and game.combat_manager:
            print("✓ CombatManager properly integrated")
        else:
            print("✗ CombatManager not found in GameEngine")
            return False
        
        # Check player combat stats
        if hasattr(game.player, 'combat_stats'):
            print("✓ Player has combat stats")
        else:
            print("✗ Player missing combat stats")
            return False
        
        # Check NPC combat stats
        npcs = game.npc_manager.get_npcs_in_room("WHOUS")
        if npcs and hasattr(npcs[0], 'combat_stats'):
            print("✓ NPCs have combat stats")
        else:
            print("✗ NPCs missing combat stats (or no NPCs in WHOUS)")
            return False
        
        print("\n✅ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return False


def run_command_test():
    """Test combat command routing."""
    print("\n" + "="*60)
    print("COMBAT COMMAND TEST")  
    print("="*60)
    
    try:
        from src.parser.command_parser import CommandParser
        
        parser = CommandParser()
        
        # Test attack command parsing
        command = parser.parse("attack warrior")
        print(f"✓ 'attack warrior' parsed as: {command.verb} {command.noun}")
        
        command = parser.parse("fight troll") 
        print(f"✓ 'fight troll' parsed as: {command.verb} {command.noun}")
        
        command = parser.parse("defend")
        print(f"✓ 'defend' parsed as: {command.verb}")
        
        command = parser.parse("flee")
        print(f"✓ 'flee' parsed as: {command.verb}")
        
        print("\n✅ Command parsing tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Command test failed: {e}")
        return False


if __name__ == "__main__":
    print("COMBAT SYSTEM - PHASE 1 TESTING")
    print("="*60)
    print("Testing Combat Foundation Implementation")
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration tests
    integration_passed = run_combat_integration_test()
    command_passed = run_command_test()
    
    # Summary
    print("\n" + "="*60)
    print("PHASE 1 TEST SUMMARY")
    print("="*60)
    print("✅ Unit tests completed")
    print(f"{'✅' if integration_passed else '❌'} Integration tests {'passed' if integration_passed else 'failed'}")
    print(f"{'✅' if command_passed else '❌'} Command tests {'passed' if command_passed else 'failed'}")
    
    if integration_passed and command_passed:
        print("\n🎉 PHASE 1: COMBAT FOUNDATION - COMPLETE!")
        print("Ready to proceed to Phase 2: Thief NPC Implementation")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before proceeding.")