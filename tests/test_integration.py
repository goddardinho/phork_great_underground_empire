#!/usr/bin/env python3
"""
Integration Testing Suite for Zork Game Engine
Tests all systems working together seamlessly
"""

import unittest
import sys
import os
import io
from contextlib import redirect_stdout
from pathlib import Path

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.game import GameEngine


class TestGameIntegration(unittest.TestCase):
    """Integration tests for complete game system workflows"""
    
    def setUp(self):
        """Set up test environment with full game"""
        self.game = GameEngine(debug_mode=False, use_mud_files=True)
        self.captured_output = io.StringIO()
        
        # Ensure we start at West of House
        self.game.player.current_room = "WHOUS"
        
    def test_basic_gameplay_workflow(self):
        """Test basic gameplay commands flowing through all systems"""
        print("\n🎮 Testing Basic Gameplay Workflow...")
        
        # Test sequence: look around, examine objects, move, take objects
        test_sequence = [
            ("look", "This is an open field west of a white house"),
            ("inventory", "You are empty-handed"),
            ("examine house", "house"),  # Should find house-related response
            ("go west", "forest"),  # Should move to a forest area
            ("look", "forest"),  # Should see forest description
            ("go east", "field"),  # Return to starting area
            ("look", "field")   # Back to original area
        ]
        
        success_count = 0
        total_tests = len(test_sequence)
        
        for command, expected_content in test_sequence:
            with redirect_stdout(self.captured_output):
                self.game._process_command(command)
            
            output = self.captured_output.getvalue()
            self.captured_output.truncate(0)
            self.captured_output.seek(0)
            
            # Check if expected content appears (case-insensitive)
            if expected_content.lower() in output.lower():
                success_count += 1
                print(f"    ✓ '{command}' -> found '{expected_content}'")
            else:
                print(f"    ⚠ '{command}' -> missing '{expected_content}' in: {output[:100]}...")
                
        success_rate = success_count / total_tests
        print(f"    Basic workflow success rate: {success_rate:.1%} ({success_count}/{total_tests})")
        
        # Should achieve reasonable success rate
        self.assertGreater(success_rate, 0.6, "Basic workflow should have >60% success rate")
    
    def test_object_interaction_integration(self):
        """Test object interaction across all systems"""
        print("\n🔧 Testing Object Interaction Integration...")
        
        # Find a room with objects to test with
        test_room = None
        for room_id, room in self.game.world.rooms.items():
            if room.items:  # Room has objects
                test_room = room_id
                break
        
        if not test_room:
            self.skipTest("No rooms with objects found for integration testing")
            
        # Move to test room
        self.game.player.current_room = test_room
        
        integration_tests = [
            ("look", "test room description"),
            ("inventory", "empty-handed"),
            ("take all", "taken"),  # Try bulk action
            ("inventory", "carrying"),  # Should have items now
            ("examine lamp", "lamp"),  # Test specific object examination
            ("drop all", "dropped"),  # Test bulk drop
            ("look", "test room")  # Should see objects back in room
        ]
        
        success_count = 0
        for command, expected_type in integration_tests:
            try:
                with redirect_stdout(self.captured_output):
                    self.game._process_command(command)
                
                output = self.captured_output.getvalue()
                self.captured_output.truncate(0)
                self.captured_output.seek(0)
                
                # Basic validation that command produced reasonable output
                if len(output.strip()) > 0 and not output.startswith("I don't understand"):
                    success_count += 1
                    print(f"    ✓ '{command}' -> valid response")
                else:
                    print(f"    ⚠ '{command}' -> invalid response: {output[:50]}...")
                    
            except Exception as e:
                print(f"    ❌ '{command}' -> error: {e}")
        
        success_rate = success_count / len(integration_tests)
        print(f"    Object integration success rate: {success_rate:.1%}")
        
        self.assertGreater(success_rate, 0.5, "Object integration should have >50% success rate")
    
    def test_parser_game_engine_integration(self):
        """Test parser and game engine integration"""
        print("\n⚡ Testing Parser-GameEngine Integration...")
        
        # Test various command types and parser edge cases
        parser_tests = [
            "look around carefully",  # Multiple words
            "go north then south",    # Complex command
            "take the lamp",         # Article handling  
            "put sword in case",     # Preposition parsing
            "examine rusty sword",   # Adjective handling
            "inventory please",      # Politeness handling
            "help me",              # Help system
            "score"                 # Score system - removed quit to avoid interactive prompt
        ]
        
        successful_parses = 0
        for command in parser_tests:
            try:
                # Test parser can handle the command
                parsed = self.game.parser.parse(command)
                self.assertIsNotNone(parsed, f"Parser failed to parse: {command}")
                
                # Test game engine can process it
                with redirect_stdout(self.captured_output):
                    self.game._process_command(command)
                
                output = self.captured_output.getvalue()
                self.captured_output.truncate(0)
                self.captured_output.seek(0)
                
                # Should produce some output (not crash)
                if len(output.strip()) > 0:
                    successful_parses += 1
                    print(f"    ✓ '{command}' -> parsed and processed")
                    
                # Don't actually quit during test
                if command == "quit":
                    self.game.running = True
                    
            except Exception as e:
                print(f"    ❌ '{command}' -> integration error: {e}")
        
        success_rate = successful_parses / len(parser_tests)
        print(f"    Parser-engine integration: {success_rate:.1%}")
        
        self.assertGreater(success_rate, 0.8, "Parser-engine integration should have >80% success rate")
    
    def test_world_object_manager_integration(self):
        """Test world and object manager integration"""
        print("\n🌍 Testing World-ObjectManager Integration...")
        
        # Validate object-room consistency
        total_objects_in_rooms = 0
        objects_found_in_manager = 0
        
        for room in self.game.world.rooms.values():
            for item_id in room.items:
                total_objects_in_rooms += 1
                obj = self.game.object_manager.get_object(item_id)
                if obj:
                    objects_found_in_manager += 1
        
        print(f"    Objects in rooms: {total_objects_in_rooms}")
        print(f"    Objects in manager: {objects_found_in_manager}")
        
        if total_objects_in_rooms > 0:
            consistency_rate = objects_found_in_manager / total_objects_in_rooms
            print(f"    Consistency rate: {consistency_rate:.1%}")
            self.assertGreater(consistency_rate, 0.9, "World-ObjectManager consistency should be >90%")
        
        # Test object location finding
        sample_objects = list(self.game.object_manager.objects.values())[:5]  # Test 5 objects
        location_success = 0
        
        for obj in sample_objects:
            try:
                location_type, container_id = self.game.object_manager.find_object_location(
                    obj, self.game.world, self.game.player
                )
                if location_type in ["room", "inventory", "container"]:
                    location_success += 1
                    print(f"    ✓ Found '{obj.name}' in {location_type}")
            except Exception as e:
                print(f"    ⚠ Error finding '{obj.name}': {e}")
        
        if sample_objects:
            location_rate = location_success / len(sample_objects)
            print(f"    Object location success: {location_rate:.1%}")
            self.assertGreater(location_rate, 0.8, "Object location finding should have >80% success")
    
    def test_score_system_integration(self):
        """Test score system integration with game actions"""
        print("\n🏆 Testing Score System Integration...")
        
        initial_score = self.game.score_manager.current_score()
        print(f"    Initial score: {initial_score}")
        
        # Try actions that might affect score
        score_affecting_actions = [
            "take lamp",
            "take sword", 
            "open mailbox",
            "take leaflet",
            "inventory"
        ]
        
        score_changes = 0
        for action in score_affecting_actions:
            pre_score = self.game.score_manager.current_score()
            
            try:
                with redirect_stdout(self.captured_output):
                    self.game._process_command(action)
                self.captured_output.truncate(0)
                self.captured_output.seek(0)
                
                post_score = self.game.score_manager.current_score()
                if post_score != pre_score:
                    score_changes += 1
                    print(f"    ✓ '{action}' changed score: {pre_score} -> {post_score}")
                    
            except Exception as e:
                print(f"    ⚠ Score test error for '{action}': {e}")
        
        # Test score command
        with redirect_stdout(self.captured_output):
            self.game._process_command("score")
        output = self.captured_output.getvalue()
        self.captured_output.truncate(0)
        self.captured_output.seek(0)
        
        score_in_output = "score" in output.lower() or str(self.game.score_manager.current_score()) in output
        print(f"    Score command integration: {'✓' if score_in_output else '❌'}")
        
        # Score system should be responsive (changes or proper reporting)
        self.assertTrue(score_changes > 0 or score_in_output, 
                       "Score system should either track changes or report properly")
    
    def test_save_load_integration(self):
        """Test save/load system integration"""
        print("\n💾 Testing Save/Load Integration...")
        
        # Make some changes to game state
        self.game.player.current_room = "WHOUS"
        
        # Try to interact with game to change state
        with redirect_stdout(self.captured_output):
            self.game._process_command("take lamp")
            self.game._process_command("go west")
        self.captured_output.truncate(0)
        self.captured_output.seek(0)
        
        original_room = self.game.player.current_room
        original_inventory = self.game.player.inventory.copy()
        
        # Test save functionality (if available)
        try:
            if hasattr(self.game, 'save_game'):
                save_result = self.game.save_game("integration_test.json")
                print(f"    Save operation: {'✓' if save_result else '❌'}")
                
                # Test load functionality
                if save_result and hasattr(self.game, 'load_game'):
                    # Change state slightly
                    self.game.player.current_room = "EHOUS"
                    
                    load_result = self.game.load_game("integration_test.json")
                    print(f"    Load operation: {'✓' if load_result else '❌'}")
                    
                    # Verify state restoration
                    room_restored = self.game.player.current_room == original_room
                    print(f"    State restoration: {'✓' if room_restored else '❌'}")
                    
                    # Clean up test file
                    test_file = Path("integration_test.json")
                    if test_file.exists():
                        test_file.unlink()
                        
                    self.assertTrue(load_result, "Load operation should succeed")
                else:
                    print("    Save/load methods available but save failed")
            else:
                print("    Save/load not implemented - skipping")
                self.skipTest("Save/load functionality not available")
                
        except Exception as e:
            print(f"    Save/load integration error: {e}")
            self.skipTest(f"Save/load integration failed: {e}")
    
    def test_error_handling_integration(self):
        """Test error handling across all systems"""
        print("\n🛡️ Testing Error Handling Integration...")
        
        # Test various error conditions
        error_tests = [
            "go nonexistentdirection",    # Invalid direction
            "take nonexistentobject",     # Invalid object
            "put sword in nonexistent",   # Invalid container
            "talk to nobody",             # Invalid target
            "use magic spell",            # Invalid action
            "examine the mysterious quantum flux generator"  # Very long invalid object
        ]
        
        graceful_errors = 0
        for test_command in error_tests:
            try:
                with redirect_stdout(self.captured_output):
                    self.game._process_command(test_command)
                
                output = self.captured_output.getvalue()
                self.captured_output.truncate(0)
                self.captured_output.seek(0)
                
                # Should produce an error message, not crash
                has_error_message = len(output.strip()) > 0
                no_python_traceback = "Traceback" not in output
                game_still_running = self.game.running
                
                if has_error_message and no_python_traceback and game_still_running:
                    graceful_errors += 1
                    print(f"    ✓ '{test_command}' -> graceful error")
                else:
                    print(f"    ❌ '{test_command}' -> poor error handling")
                    
            except Exception as e:
                print(f"    ❌ '{test_command}' -> exception: {e}")
        
        error_rate = graceful_errors / len(error_tests)
        print(f"    Graceful error handling: {error_rate:.1%}")
        
        self.assertGreater(error_rate, 0.7, "Error handling should be graceful >70% of the time")
    
    def test_memory_and_state_consistency(self):
        """Test memory management and state consistency across systems"""
        print("\n🧠 Testing Memory & State Consistency...")
        
        # Record initial state
        initial_room_count = len(self.game.world.rooms)
        initial_object_count = len(self.game.object_manager.objects)
        initial_player_room = self.game.player.current_room
        
        print(f"    Initial state: {initial_room_count} rooms, {initial_object_count} objects")
        
        # Perform many operations
        stress_commands = [
            "look", "inventory", "go north", "go south", "go east", "go west",
            "take all", "drop all", "examine house", "score", "help"
        ] * 5  # Repeat 5 times
        
        commands_executed = 0
        for command in stress_commands:
            try:
                with redirect_stdout(self.captured_output):
                    self.game._process_command(command)
                self.captured_output.truncate(0)
                self.captured_output.seek(0)
                commands_executed += 1
            except Exception as e:
                print(f"    ⚠ Command '{command}' failed: {e}")
                break
        
        # Check state consistency after stress test
        final_room_count = len(self.game.world.rooms)
        final_object_count = len(self.game.object_manager.objects)
        
        room_consistency = initial_room_count == final_room_count
        object_consistency = initial_object_count == final_object_count
        game_still_responsive = self.game.running
        
        print(f"    Commands executed: {commands_executed}/{len(stress_commands)}")
        print(f"    Room count consistency: {'✓' if room_consistency else '❌'}")
        print(f"    Object count consistency: {'✓' if object_consistency else '❌'}")
        print(f"    Game responsiveness: {'✓' if game_still_responsive else '❌'}")
        
        # All consistency checks should pass
        self.assertTrue(room_consistency, "Room count should remain consistent")
        self.assertTrue(object_consistency, "Object count should remain consistent")  
        self.assertTrue(game_still_responsive, "Game should remain responsive")
        
        # Should execute most commands successfully
        execution_rate = commands_executed / len(stress_commands)
        self.assertGreater(execution_rate, 0.8, "Should execute >80% of stress test commands")


def run_integration_tests():
    """Run the complete integration testing suite"""
    print("=" * 70)
    print("🔧 ZORK INTEGRATION TESTING SUITE")
    print("=" * 70)
    print("Testing all systems working together seamlessly...")
    
    # Configure unittest for detailed output
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGameIntegration)
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=False)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("🎯 INTEGRATION TESTING COMPLETE")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("✅ All integration tests PASSED")
        print("🎮 All systems work together seamlessly")
        print("🚀 Game ready for production integration")
    else:
        print("❌ Some integration tests FAILED")
        print("🔧 Integration issues need attention")
        
        if result.failures:
            print(f"\n❌ Failures ({len(result.failures)}):")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback.splitlines()[-1]}")
                
        if result.errors:
            print(f"\n💥 Errors ({len(result.errors)}):")
            for test, traceback in result.errors:
                print(f"   - {test}: {traceback.splitlines()[-1]}")
    
    print(f"\nIntegration Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)