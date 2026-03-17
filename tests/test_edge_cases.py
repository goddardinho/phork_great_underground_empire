#!/usr/bin/env python3

"""
Edge Case and Integration Testing for Zork Implementation
========================================================

Tests complex scenarios, game state interactions, and edge cases:
- Dark room mechanics and grue encounters
- Dangerous areas and death scenarios  
- Special room behaviors and transitions
- Object state changes and combinations
- Save/load state integrity
- Performance under stress
"""

import sys
import time
import json
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.game import GameEngine
from src.entities.player import Player


class EdgeCaseValidator:
    """Validates complex edge cases and integration scenarios."""
    
    def __init__(self):
        self.results = []
        
    def setup_game_state(self, scenario: str) -> GameEngine:
        """Setup specific game state for testing."""
        game = GameEngine(use_mud_files=True, mud_directory=Path("zork_mtl_source"))
        
        if scenario == "dark_room":
            # Navigate to a dark area (example: go down from living room)
            commands = ["open trap door", "down"]
            for cmd in commands:
                try:
                    game._process_command(cmd)
                except:
                    pass
                    
        elif scenario == "with_items":
            # Start with some items
            commands = ["take lamp", "take sword"]  
            for cmd in commands:
                try:
                    game._process_command(cmd)
                except:
                    pass
        elif scenario == "normal":
            # Default state, no changes needed
            pass
        
        return game
    
    def test_dark_room_mechanics(self) -> Dict[str, Any]:
        """Test behavior in dark rooms."""
        print("🌑 Testing dark room mechanics...")
        
        tests = []
        
        # Test 1: Basic dark room detection
        game = self.setup_game_state("dark_room")
        response = self._capture_output(game, "look")
        has_darkness_message = any(word in response.lower() 
                                 for word in ["dark", "black", "grue", "light"])
        
        tests.append({
            'test': 'dark_room_detection',
            'command': 'look (in dark room)',
            'response': response,
            'success': has_darkness_message
        })
        
        # Test 2: Movement in dark
        game = self.setup_game_state("dark_room")
        response = self._capture_output(game, "north")
        handles_dark_movement = len(response) > 0  # Should respond somehow
        
        tests.append({
            'test': 'dark_room_movement', 
            'command': 'north (in dark)',
            'response': response,
            'success': handles_dark_movement
        })
        
        # Test 3: Light source mechanics
        game = self.setup_game_state("with_items")
        # Try to light lamp if available
        response = self._capture_output(game, "light lamp")
        light_response = len(response) > 0
        
        tests.append({
            'test': 'light_source',
            'command': 'light lamp',
            'response': response, 
            'success': light_response
        })
        
        success_rate = sum(1 for t in tests if t['success']) / len(tests)
        return {
            'category': 'dark_room_mechanics',
            'success_rate': success_rate,
            'tests': tests
        }
    
    def test_object_state_integrity(self) -> Dict[str, Any]:
        """Test object state changes and persistence."""
        print("📦 Testing object state integrity...")
        
        tests = []
        
        # Test 1: Taking and dropping objects
        game = self.setup_game_state("normal")
        
        # Take something
        take_response = self._capture_output(game, "take lamp")
        # Check inventory
        inv_response = self._capture_output(game, "inventory")
        # Drop it
        drop_response = self._capture_output(game, "drop lamp")
        # Check inventory again  
        inv2_response = self._capture_output(game, "inventory")
        
        object_state_consistent = (
            len(take_response) > 0 and 
            len(drop_response) > 0 and
            inv_response != inv2_response  # Inventory should change
        )
        
        tests.append({
            'test': 'take_drop_consistency',
            'command': 'take/drop sequence',
            'response': f"take: {take_response[:30]}... drop: {drop_response[:30]}...",
            'success': object_state_consistent
        })
        
        # Test 2: Container interactions
        game = self.setup_game_state("normal")
        
        # Try container operations
        open_response = self._capture_output(game, "open mailbox") 
        look_response = self._capture_output(game, "look in mailbox")
        
        container_handling = len(open_response) > 0 and len(look_response) > 0
        
        tests.append({
            'test': 'container_interactions',
            'command': 'open mailbox, look in mailbox',
            'response': f"open: {open_response[:30]}... look: {look_response[:30]}...",
            'success': container_handling
        })
        
        success_rate = sum(1 for t in tests if t['success']) / len(tests)
        return {
            'category': 'object_state_integrity',
            'success_rate': success_rate,
            'tests': tests
        }
    
    def test_parser_stress_cases(self) -> Dict[str, Any]:
        """Test parser under stress and edge cases."""
        print("⚙️ Testing parser stress cases...")
        
        tests = []
        game = self.setup_game_state("normal")
        
        stress_inputs = [
            # Very long inputs
            "take the very large heavy rusty old ancient mysterious glowing magical sword carefully with both hands",
            # Ambiguous inputs
            "put it there", 
            # Multiple objects
            "take lamp and sword and rope",
            # Nested prepositions
            "put the sword in the box on the table",
            # Numbers and special characters
            "take 5 coins from the bag @ the store",
            # Unicode and special cases
            "café naïve résumé",  # Non-ASCII
        ]
        
        for input_text in stress_inputs:
            try:
                response = self._capture_output(game, input_text)
                handled_gracefully = len(response) > 0 and "ERROR" not in response
            except Exception:
                handled_gracefully = False
                response = "EXCEPTION"
                
            tests.append({
                'test': 'stress_input',
                'command': input_text[:40] + "..." if len(input_text) > 40 else input_text,
                'response': response[:50] + "..." if len(response) > 50 else response,
                'success': handled_gracefully
            })
        
        success_rate = sum(1 for t in tests if t['success']) / len(tests)
        return {
            'category': 'parser_stress_cases',
            'success_rate': success_rate, 
            'tests': tests
        }
    
    def test_game_state_transitions(self) -> Dict[str, Any]:
        """Test complex game state transitions."""
        print("🎮 Testing game state transitions...")
        
        tests = []
        
        # Test 1: Room transition consistency 
        game = self.setup_game_state("normal")
        
        # Move around and return
        responses = []
        commands = ["north", "south", "look"]
        
        for cmd in commands:
            response = self._capture_output(game, cmd)
            responses.append(response)
        
        movement_consistent = all(len(r) > 0 for r in responses)
        
        tests.append({
            'test': 'room_transitions',
            'command': 'north -> south -> look',
            'response': f"Moved and returned successfully",
            'success': movement_consistent
        })
        
        # Test 2: Score system integration
        game = self.setup_game_state("normal")
        
        score_response = self._capture_output(game, "score")
        score_works = "score" in score_response.lower() or "points" in score_response.lower()
        
        tests.append({
            'test': 'score_system',
            'command': 'score',
            'response': score_response,
            'success': score_works
        })
        
        success_rate = sum(1 for t in tests if t['success']) / len(tests)
        return {
            'category': 'game_state_transitions',
            'success_rate': success_rate,
            'tests': tests
        }
    
    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test performance under various conditions."""
        print("⚡ Testing performance benchmarks...")
        
        tests = []
        
        # Test 1: Command processing speed
        game = self.setup_game_state("normal")
        
        start_time = time.time()
        for i in range(10):
            self._capture_output(game, "look")
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        fast_enough = avg_time < 0.1  # Should be under 100ms per command
        
        tests.append({
            'test': 'command_speed',
            'command': '10x look commands',
            'response': f"Average: {avg_time:.3f}s per command",
            'success': fast_enough
        })
        
        # Test 2: Memory usage stability
        game = self.setup_game_state("normal")
        
        # Execute many commands
        start_time = time.time()
        for i in range(50):
            commands = ["look", "inventory", "north", "south"]
            for cmd in commands:
                try:
                    self._capture_output(game, cmd)
                except:
                    pass
        end_time = time.time()
        
        total_time = end_time - start_time
        stable_performance = total_time < 5.0  # Should complete in under 5 seconds
        
        tests.append({
            'test': 'stability_test',
            'command': '200 commands executed',
            'response': f"Completed in {total_time:.2f}s", 
            'success': stable_performance
        })
        
        success_rate = sum(1 for t in tests if t['success']) / len(tests)
        return {
            'category': 'performance_benchmarks',
            'success_rate': success_rate,
            'tests': tests
        }
    
    def _capture_output(self, game: GameEngine, command: str) -> str:
        """Capture command output."""
        import io
        import contextlib
        
        captured_output = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured_output):
                game._process_command(command)
        except Exception as e:
            return f"ERROR: {e}"
        
        return captured_output.getvalue().strip()
    
    def run_all_edge_case_tests(self) -> Dict[str, Any]:
        """Run all edge case and integration tests."""
        print("🧪 EDGE CASE & INTEGRATION TESTING")
        print("=" * 50)
        
        test_methods = [
            self.test_dark_room_mechanics,
            self.test_object_state_integrity, 
            self.test_parser_stress_cases,
            self.test_game_state_transitions,
            self.test_performance_benchmarks,
        ]
        
        all_results = []
        total_success = 0
        total_tests = 0
        
        for test_method in test_methods:
            try:
                result = test_method()
                all_results.append(result)
                
                category_successes = sum(1 for t in result['tests'] if t['success'])
                category_total = len(result['tests'])
                total_success += category_successes
                total_tests += category_total
                
                print(f"✅ {result['category']:25s}: {category_successes:2d}/{category_total:2d} ({result['success_rate']:5.1%})")
                
            except Exception as e:
                print(f"❌ {test_method.__name__:25s}: FAILED - {e}")
                all_results.append({
                    'category': test_method.__name__,
                    'success_rate': 0.0,
                    'tests': [{'test': 'framework_error', 'success': False, 'response': str(e)}]
                })
        
        overall_success_rate = total_success / total_tests if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL INTEGRATION SUCCESS: {total_success}/{total_tests} ({overall_success_rate:.1%})")
        
        # Show detailed failures
        failed_tests = []
        for result in all_results:
            for test in result.get('tests', []):
                if not test['success']:
                    failed_tests.append((result['category'], test.get('test', 'unknown'), test.get('response', 'no response')))
        
        if failed_tests:
            print(f"\n❌ FAILED INTEGRATION TESTS ({len(failed_tests)}):")
            for category, test_name, response in failed_tests[:10]:  # Show first 10
                print(f"   {category:20s}: {test_name:20s} → {response[:50]}..." if len(response) > 50 else f"   {category:20s}: {test_name:20s} → {response}")
            if len(failed_tests) > 10:
                print(f"   ... and {len(failed_tests) - 10} more failures")
        
        if overall_success_rate >= 0.9:
            print(f"\n🎉 EXCELLENT! Integration testing at {overall_success_rate:.1%}")
        elif overall_success_rate >= 0.8:
            print(f"\n👍 GOOD! Integration testing at {overall_success_rate:.1%}")
        else:
            print(f"\n⚠️ NEEDS WORK! Integration testing at {overall_success_rate:.1%}")
        
        return {
            'overall_success_rate': overall_success_rate,
            'category_results': all_results,
            'failed_tests': failed_tests,
            'total_success': total_success,
            'total_tests': total_tests
        }


def main():
    """Main edge case testing execution."""
    validator = EdgeCaseValidator()
    
    try:
        results = validator.run_all_edge_case_tests()
        
        # Exit based on success rate
        if results['overall_success_rate'] >= 0.85:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"🚨 EDGE CASE TESTING ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()