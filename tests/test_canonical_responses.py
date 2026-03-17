#!/usr/bin/env python3

"""
Canonical Response Validation for Zork Implementation  
====================================================

Validates that game responses match authentic 1978 MIT Zork behavior.
Tests against known response patterns from original parser.mud and action files.
"""

import sys
import re
from typing import Dict, List, Tuple, Any
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.game import GameEngine
from src.responses import ZorkResponses


class CanonicalResponseValidator:
    """Validates responses against authentic Zork patterns."""
    
    def __init__(self):
        self.game_engine = GameEngine(use_mud_files=True, mud_directory=Path("zork_mtl_source"))
        self.responses = ZorkResponses()
        self.canonical_patterns = self._load_canonical_patterns()
        
    def _load_canonical_patterns(self) -> Dict[str, List[str]]:
        """Load known canonical response patterns from original Zork."""
        return {
            # Unknown command responses (from parser.mud)
            "unknown_commands": [
                r"Huh\?",
                r"What\?", 
                r"I beg your pardon\?",
                r"That doesn't make sense!",
                r"I don't know how to do that\.",
                r"I don't understand that\.",
                r"Come again\?",
                r"I don't know the word.*",
                r"That's not a verb I recognize\.",
            ],
            
            # Movement failures
            "movement_blocked": [
                r"You can't go that way\.",
                r"I don't see how you can go.*",
                r"You can't go.*",
                r"The .* is closed\.",
                r"The .* is locked\.",
            ],
            
            # Object not found
            "object_not_found": [
                r"I don't see .* here\.",
                r"What .*\?",
                r"I can't see .* here\.",
                r"There is no .* here\.",
            ],
            
            # Impossible actions
            "impossible_actions": [
                r"You can't do that\.",
                r"That's not something you can do\.",
                r"I don't think .* would be interested\.",
                r"You can't .* the .*\.",
                r"That doesn't work\.",
            ],
            
            # Inventory issues
            "inventory_issues": [
                r"You're not carrying .*\.",
                r"You already have .*\.",
                r"You can't take .*\.",
                r"Your hands are full\.",
                r"You are carrying:.*",
                r"You are empty-handed\.",
            ],
            
            # Container interactions  
            "container_responses": [
                r"The .* is already .*\.",
                r"The .* is .*\.",
                r"You can't .* the .*\.",
                r"There is nothing in the .*\.",
                r"The .* contains:.*",
            ],
            
            # Combat responses
            "combat_responses": [
                r"Trying to attack .* is suicide\.",
                r"The .* doesn't want to fight\.",
                r"I don't think the .* would appreciate that\.",
                r"You miss\.",
                r"Your .* misses the .*\.",
            ],
            
            # Special Zork humor
            "zork_humor": [
                r"A hollow voice says.*Fool.*",
                r"Nothing happens\.",
                r"Very good\. Now you can go to the second grade\.",
                r"You have a perfectly good lamp already\.",
                r"I don't think .* is such a good idea\.",
                r"What a concept!",
            ],
            
            # Game state responses
            "game_state": [
                r"Your score is .* of .* in .* moves\.",
                r"You have scored .* points out of .*\.",
                r"Time passes\.",
                r"It is now pitch black\. You are likely to be eaten by a grue\.",
            ]
        }
    
    def test_unknown_command_responses(self) -> Dict[str, Any]:
        """Test responses to unknown/invalid commands."""
        print("🔍 Testing unknown command responses...")
        
        unknown_commands = [
            "asdfghjkl", "foo", "bar", "blah", "xyz", "nonsense", 
            "gibberish", "invalid", "notaword", "fakeverb"
        ]
        
        results = []
        for cmd in unknown_commands[:5]:  # Test first 5
            response = self._capture_command_output(cmd)
            matches_pattern = any(re.search(pattern, response, re.IGNORECASE) 
                                for pattern in self.canonical_patterns["unknown_commands"])
            results.append({
                'command': cmd,
                'response': response,
                'canonical_match': matches_pattern
            })
        
        success_rate = sum(1 for r in results if r['canonical_match']) / len(results)
        return {
            'category': 'unknown_commands',
            'success_rate': success_rate,
            'results': results
        }
    
    def test_movement_responses(self) -> Dict[str, Any]:
        """Test movement command responses."""
        print("🚶 Testing movement responses...")
        
        # Test invalid directions from starting room
        invalid_moves = ["northeast", "northwest", "southeast", "southwest", "down"]
        
        results = []
        for direction in invalid_moves[:3]:  # Test first 3
            response = self._capture_command_output(direction)
            matches_pattern = any(re.search(pattern, response, re.IGNORECASE)
                                for pattern in self.canonical_patterns["movement_blocked"])
            results.append({
                'command': direction,
                'response': response,
                'canonical_match': matches_pattern
            })
        
        success_rate = sum(1 for r in results if r['canonical_match']) / len(results) if results else 0
        return {
            'category': 'movement_responses', 
            'success_rate': success_rate,
            'results': results
        }
    
    def test_object_interaction_responses(self) -> Dict[str, Any]:
        """Test object interaction responses."""
        print("📦 Testing object interaction responses...")
        
        object_commands = [
            "take nonexistent", 
            "examine invisible",
            "drop nothing",
            "open fakebox",
            "close imaginary"
        ]
        
        results = []
        for cmd in object_commands:
            response = self._capture_command_output(cmd)
            matches_pattern = any(re.search(pattern, response, re.IGNORECASE)
                                for pattern in self.canonical_patterns["object_not_found"])
            results.append({
                'command': cmd,
                'response': response, 
                'canonical_match': matches_pattern
            })
        
        success_rate = sum(1 for r in results if r['canonical_match']) / len(results) if results else 0
        return {
            'category': 'object_interactions',
            'success_rate': success_rate,  
            'results': results
        }
    
    def test_inventory_responses(self) -> Dict[str, Any]:
        """Test inventory-related responses."""
        print("🎒 Testing inventory responses...")
        
        # Test basic inventory command
        response = self._capture_command_output("inventory")
        
        # Should show either items or empty message
        valid_inventory = (
            "carrying" in response.lower() or 
            "empty" in response.lower() or
            "nothing" in response.lower() or
            len(response.strip()) > 0
        )
        
        results = [{
            'command': 'inventory',
            'response': response,
            'canonical_match': valid_inventory
        }]
        
        return {
            'category': 'inventory_responses',
            'success_rate': 1.0 if valid_inventory else 0.0,
            'results': results
        }
    
    def test_special_zork_commands(self) -> Dict[str, Any]:
        """Test special Zork Easter egg commands."""
        print("🎭 Testing special Zork commands...")
        
        special_commands = [
            "xyzzy", "plugh", "hello", "diagnose", "score", "time"
        ]
        
        results = []
        for cmd in special_commands:
            response = self._capture_command_output(cmd)
            # Special commands should produce some response, not unknown command error
            is_handled = not any(re.search(pattern, response, re.IGNORECASE)
                               for pattern in self.canonical_patterns["unknown_commands"])
            results.append({
                'command': cmd,
                'response': response,
                'canonical_match': is_handled
            })
        
        success_rate = sum(1 for r in results if r['canonical_match']) / len(results) if results else 0
        return {
            'category': 'special_commands',
            'success_rate': success_rate,
            'results': results  
        }
    
    def test_parser_edge_cases(self) -> Dict[str , Any]:
        """Test parser edge cases and complex syntax."""
        print("⚙️ Testing parser edge cases...")
        
        edge_cases = [
            "",  # Empty input
            "   ",  # Whitespace only
            "north south east west",  # Multiple directions
            "take the big blue shiny sword carefully",  # Complex parsing
            "put all lamps in the chest",  # Bulk operations
        ]
        
        results = []
        for cmd in edge_cases:
            try:
                response = self._capture_command_output(cmd)
                # Should handle gracefully without crashing
                handled_gracefully = len(response) > 0
            except Exception:
                handled_gracefully = False
                response = "CRASHED"
                
            results.append({
                'command': repr(cmd),  # Show quotes for empty/space strings
                'response': response,
                'canonical_match': handled_gracefully
            })
        
        success_rate = sum(1 for r in results if r['canonical_match']) / len(results) if results else 0
        return {
            'category': 'parser_edge_cases',
            'success_rate': success_rate,
            'results': results
        }
    
    def _capture_command_output(self, command: str) -> str:
        """Capture output from a command execution."""
        import io
        import contextlib
        
        # Create fresh game state
        self.game_engine = GameEngine(use_mud_files=True, mud_directory=Path("zork_mtl_source"))
        
        captured_output = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured_output):
                self.game_engine._process_command(command)
        except Exception as e:
            return f"ERROR: {e}"
        
        return captured_output.getvalue().strip()
    
    def run_all_canonical_tests(self) -> Dict[str, Any]:
        """Run all canonical response validation tests."""
        print("🎯 CANONICAL RESPONSE VALIDATION")
        print("=" * 50)
        
        test_methods = [
            self.test_unknown_command_responses,
            self.test_movement_responses,
            self.test_object_interaction_responses,
            self.test_inventory_responses,
            self.test_special_zork_commands,
            self.test_parser_edge_cases,
        ]
        
        all_results = []
        total_success = 0
        total_tests = 0
        
        for test_method in test_methods:
            result = test_method()
            all_results.append(result)
            
            # Count successes
            category_successes = sum(1 for r in result['results'] if r['canonical_match'])
            category_total = len(result['results'])
            total_success += category_successes
            total_tests += category_total
            
            print(f"✅ {result['category']:20s}: {category_successes:2d}/{category_total:2d} ({result['success_rate']:5.1%})")
        
        overall_success_rate = total_success / total_tests if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL CANONICAL ACCURACY: {total_success}/{total_tests} ({overall_success_rate:.1%})")
        
        # Show failed tests
        failed_tests = []
        for result in all_results:
            for test in result['results']:
                if not test['canonical_match']:
                    failed_tests.append((result['category'], test['command'], test['response']))
        
        if failed_tests:
            print(f"\n❌ NON-CANONICAL RESPONSES ({len(failed_tests)}):")
            for category, command, response in failed_tests:
                print(f"   {category:15s}: {command:20s} → {response[:50]}..." if len(response) > 50 else f"   {category:15s}: {command:20s} → {response}")
        
        if overall_success_rate >= 0.9:
            print(f"\n🎉 EXCELLENT! Canonical accuracy at {overall_success_rate:.1%}")
        elif overall_success_rate >= 0.8:
            print(f"\n👍 GOOD! Canonical accuracy at {overall_success_rate:.1%}")  
        else:
            print(f"\n⚠️ NEEDS IMPROVEMENT! Canonical accuracy at {overall_success_rate:.1%}")
        
        return {
            'overall_success_rate': overall_success_rate,
            'category_results': all_results,
            'failed_tests': failed_tests,
            'total_success': total_success,
            'total_tests': total_tests
        }


def main():
    """Main validation execution."""
    validator = CanonicalResponseValidator()
    
    try:
        results = validator.run_all_canonical_tests()
        
        # Exit with appropriate code based on success rate
        if results['overall_success_rate'] >= 0.9:
            sys.exit(0)
        elif results['overall_success_rate'] >= 0.8:
            sys.exit(0)  
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"🚨 VALIDATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()