"""Tests for Thief NPC - Phase 2 of Canonical NPCs Feature

Tests covering:
- Thief creation and initialization
- Theft mechanics and object stealing  
- Movement behaviors and room traversal
- Combat integration and loot dropping
- Player interaction flows

All tests validate authentic Zork Thief behaviors.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
import sys
from pathlib import Path

# Add the src directory to the path so we can import the modules
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from entities.thief import (
    ThiefBehavior, 
    create_canonical_thief, 
    integrate_thief_behaviors,
    _handle_thief_behaviors,
    _handle_thief_movement
)
from entities.npc import NPC
from entities.objects import GameObject  
from entities.object_manager import ObjectManager
from entities.player import Player
from entities.combat import CombatStats
from world.world import World
from world.room import Room


class TestThiefBehavior(unittest.TestCase):
    """Test the ThiefBehavior class mechanics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_npc = Mock(spec=NPC)
        self.mock_npc.id = "THIEF"
        self.mock_npc.name = "thief"
        
        self.behavior = ThiefBehavior(self.mock_npc)
        
        # Create mock object manager
        self.object_manager = Mock(spec=ObjectManager)
        
    def test_cooldown_mechanics(self):
        """Test theft cooldown functionality."""
        # Initially should be able to attempt theft
        self.assertTrue(self.behavior.can_attempt_theft())
        
        # After setting last_theft_time to now, should be on cooldown
        self.behavior.last_theft_time = time.time()
        self.assertFalse(self.behavior.can_attempt_theft())
        
        # After cooldown period, should be able to attempt again
        self.behavior.last_theft_time = time.time() - 35  # 35 seconds ago
        self.assertTrue(self.behavior.can_attempt_theft())
    
    def test_movement_cooldown(self):
        """Test movement timing mechanics."""
        # Initially should be able to move  
        self.assertTrue(self.behavior.can_move())
        
        # After setting movement_timer, should be on cooldown
        self.behavior.movement_timer = time.time()
        self.assertFalse(self.behavior.can_move())
        
        # After movement interval, should be able to move
        self.behavior.movement_timer = time.time() - 50  # 50 seconds ago
        self.assertTrue(self.behavior.can_move())
    
    def test_theft_target_prioritization(self):
        """Test that Thief prioritizes treasures and valuable items."""
        # Create mock objects with different priorities
        treasure_obj = Mock()
        treasure_obj.name = "golden chalice"
        treasure_obj.get_attribute = Mock(side_effect=lambda attr, default=None: {
            "treasure_value": 20,
            "valuable": False,
            "weapon": False,
            "tool": False
        }.get(attr, default))
        
        weapon_obj = Mock()
        weapon_obj.name = "rusty sword"
        weapon_obj.get_attribute = Mock(side_effect=lambda attr, default=None: {
            "treasure_value": 0,
            "valuable": False,
            "weapon": True,
            "tool": False
        }.get(attr, default))
        
        junk_obj = Mock()
        junk_obj.name = "old rag"
        junk_obj.get_attribute = Mock(side_effect=lambda attr, default=None: {
            "treasure_value": 0,
            "valuable": False,
            "weapon": False,
            "tool": False
        }.get(attr, default))
        
        # Set up object manager to return these objects
        self.object_manager.get_object = Mock(side_effect=lambda obj_id: {
            "CHALICE": treasure_obj,
            "SWORD": weapon_obj,
            "RAG": junk_obj
        }.get(obj_id))
        
        # Test prioritization
        targets = self.behavior.get_theft_targets(
            ["RAG", "SWORD", "CHALICE"], 
            self.object_manager
        )
        
        # Treasure should be first priority
        self.assertEqual(targets[0], "CHALICE")
        self.assertEqual(targets[1], "SWORD") 
        self.assertEqual(targets[2], "RAG")
    
    def test_successful_theft(self):
        """Test successful object theft."""
        # Enable theft attempt
        self.behavior.last_theft_time = 0
        
        # Create mock treasure object
        treasure_obj = Mock()
        treasure_obj.name = "valuable gem"
        treasure_obj.get_attribute = Mock(side_effect=lambda attr, default=None: {
            "treasure_value": 15
        }.get(attr, default))
        
        self.object_manager.get_object = Mock(return_value=treasure_obj)
        
        # Mock random to force successful theft
        with patch('entities.thief.random.random', return_value=0.5):  # 50% < 60% success rate
            stolen = self.behavior.attempt_theft(["GEM"], self.object_manager)
            
        self.assertEqual(stolen, "GEM")
        self.assertIn("GEM", self.behavior.stolen_objects)
        self.assertGreater(self.behavior.last_theft_time, 0)
    
    def test_failed_theft(self):
        """Test failed theft attempt."""
        # Enable theft attempt
        self.behavior.last_theft_time = 0
        
        # Create mock object
        obj = Mock()
        obj.name = "test item"  # Add name property
        obj.get_attribute = Mock(return_value=0)
        self.object_manager.get_object = Mock(return_value=obj)
        
        # Mock random to force failed theft
        with patch('entities.thief.random.random', return_value=0.8):  # 80% > 60% success rate
            stolen = self.behavior.attempt_theft(["ITEM"], self.object_manager)
            
        self.assertIsNone(stolen)
        self.assertEqual(len(self.behavior.stolen_objects), 0)
    
    def test_loot_dropping(self):
        """Test loot dropping on death."""
        # Add some stolen items
        self.behavior.stolen_objects = ["SWORD", "GEM", "LANTERN"]
        
        loot = self.behavior.drop_loot_on_death()
        
        self.assertEqual(set(loot), {"SWORD", "GEM", "LANTERN"})
        self.assertEqual(len(self.behavior.stolen_objects), 0)  # Should be cleared
    
    def test_flee_decision_logic(self):
        """Test when Thief should flee from combat."""
        # High health - should not flee
        self.assertFalse(self.behavior.should_flee_combat(90, 100))
        
        # Critical health - should always flee  
        self.assertTrue(self.behavior.should_flee_combat(25, 100))
        
        # Medium health - test random component with mocking
        with patch('entities.thief.random.random', return_value=0.1):  # Force flee
            self.assertTrue(self.behavior.should_flee_combat(50, 100))
            
        with patch('entities.thief.random.random', return_value=0.5):  # Force no flee
            self.assertFalse(self.behavior.should_flee_combat(50, 100))


class TestThiefCreation(unittest.TestCase):
    """Test Thief NPC creation and initialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_npc_manager = Mock()
        
    def test_canonical_thief_creation(self):
        """Test that canonical Thief is created properly."""
        thief = create_canonical_thief(self.mock_npc_manager, "TEST_ROOM")
        
        # Validate basic properties
        self.assertEqual(thief.id, "THIEF")
        self.assertEqual(thief.name, "thief")
        self.assertEqual(thief.location, "TEST_ROOM")
        self.assertTrue(thief.get_attribute("canonical"))
        self.assertTrue(thief.get_attribute("steals_objects"))
        self.assertTrue(thief.get_attribute("drops_loot_on_death"))
        
        # Validate aliases
        expected_aliases = ["robber", "bandit", "rogue", "thief"]
        self.assertEqual(set(thief.aliases), set(expected_aliases))
        
        # Validate combat stats
        self.assertIsNotNone(thief.combat_stats)
        self.assertEqual(thief.combat_stats.max_health, 100)
        self.assertEqual(thief.combat_stats.attack_power, 18)
        self.assertGreaterEqual(thief.combat_stats.accuracy, 80)
        
        # Validate behavior system
        self.assertTrue(hasattr(thief, 'thief_behavior'))
        self.assertIsInstance(thief.thief_behavior, ThiefBehavior)
        
        # Validate dialogue tree
        self.assertIn("encounter", thief.dialogue_tree)
        self.assertIn("combat_taunt", thief.dialogue_tree) 
        self.assertIn("negotiation", thief.dialogue_tree)
        self.assertIn("dismissal", thief.dialogue_tree)


class TestThiefGameIntegration(unittest.TestCase):
    """Test Thief integration with game engine."""
    
    def setUp(self):
        """Set up test game engine mock."""
        self.mock_game_engine = Mock()
        self.mock_player = Mock()
        self.mock_object_manager = Mock()
        self.mock_npc_manager = Mock()
        
        self.mock_game_engine.player = self.mock_player
        self.mock_game_engine.object_manager = self.mock_object_manager
        self.mock_game_engine.npc_manager = self.mock_npc_manager
        
        # Set up mock player
        self.mock_player.current_room = "TEST_ROOM" 
        self.mock_player.inventory = ["LAMP", "SWORD"]
        self.mock_player.remove_from_inventory = Mock()
        
    def test_thief_behavior_integration(self):
        """Test that Thief behaviors are integrated into game engine."""
        # Create a Thief with behavior
        thief = create_canonical_thief(Mock(), "TEST_ROOM")
        thief.thief_behavior.last_theft_time = 0  # Enable theft
        
        # Mock object for theft
        mock_obj = Mock()
        mock_obj.name = "brass lantern"
        mock_obj.get_attribute = Mock(side_effect=lambda attr, default=None: {
            "treasure_value": 0,
            "tool": True
        }.get(attr, default))
        
        self.mock_object_manager.get_object = Mock(return_value=mock_obj)
        self.mock_npc_manager.get_npc = Mock(return_value=thief)
        
        # Mock successful theft
        with patch('entities.thief.random.random', return_value=0.5):
            with patch('builtins.print') as mock_print:
                _handle_thief_behaviors(self.mock_game_engine, thief)
                
                # Verify theft occurred
                self.mock_player.remove_from_inventory.assert_called_with("LAMP")
                mock_print.assert_called()
                
                # Check that item was added to Thief's stolen goods
                self.assertIn("LAMP", thief.thief_behavior.stolen_objects)
    
    def test_thief_movement_behavior(self):
        """Test Thief movement between rooms."""
        # Create world with rooms
        mock_world = Mock()
        source_room = Mock()
        source_room.exits = {"north": "DEST_ROOM", "east": "OTHER_ROOM"}
        dest_room = Mock()
        dest_room.has_flag = Mock(return_value=False)  # Not deadly
        
        mock_world.get_room = Mock(side_effect=lambda room_id: {
            "SOURCE_ROOM": source_room,
            "DEST_ROOM": dest_room,
            "OTHER_ROOM": dest_room
        }.get(room_id))
        
        self.mock_game_engine.world = mock_world
        

        # Create Thief
        thief = create_canonical_thief(Mock(), "SOURCE_ROOM")
        thief.thief_behavior.movement_timer = 0  # Enable movement
        self.mock_npc_manager.move_npc = Mock()
        
        # Test movement
        with patch('entities.thief.random.random', return_value=0.2):  # Force movement
            with patch('entities.thief.random.choice', return_value="DEST_ROOM"):
                _handle_thief_movement(self.mock_game_engine, thief)
                
                # Verify NPC was moved
                self.mock_npc_manager.move_npc.assert_called_with("THIEF", "DEST_ROOM")
                self.assertEqual(thief.location, "DEST_ROOM")


class TestThiefCombatIntegration(unittest.TestCase):
    """Test Thief-specific combat behaviors."""
    
    def test_death_loot_dropping(self):
        """Test that Thief drops loot when killed in combat."""
        # Create Thief with stolen items
        thief = create_canonical_thief(Mock())
        thief.thief_behavior.stolen_objects = ["SWORD", "LAMP"]
        
        # Mock objects for loot dropping
        sword_obj = Mock()
        sword_obj.name = "sword"
        lamp_obj = Mock() 
        lamp_obj.name = "lantern"
        
        mock_object_manager = Mock()
        mock_object_manager.get_object = Mock(side_effect=lambda obj_id: {
            "SWORD": sword_obj,
            "LAMP": lamp_obj
        }.get(obj_id))
        
        # Mock room for item placement
        mock_room = Mock()
        mock_world = Mock()
        mock_world.get_room = Mock(return_value=mock_room)
        
        # Mock game engine
        mock_game_engine = Mock()
        mock_game_engine.object_manager = mock_object_manager
        mock_game_engine.world = mock_world
        mock_game_engine.player.current_room = "TEST_ROOM"
        
        # Simulate Thief death
        thief.combat_stats = Mock()
        thief.combat_stats.is_alive = Mock(return_value=False)
        
        # Test loot dropping logic
        behavior = thief.thief_behavior
        loot = behavior.drop_loot_on_death()
        
        self.assertEqual(set(loot), {"SWORD", "LAMP"})
        self.assertEqual(len(behavior.stolen_objects), 0)


if __name__ == '__main__':
    # Set up test environment
    unittest.main(verbosity=2)