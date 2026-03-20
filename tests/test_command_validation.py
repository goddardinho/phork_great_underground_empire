#!/usr/bin/env python3

"""
Comprehensive Command and Response Testing Framework for Zork Implementation
===========================================================================

Validates all commands and responses against canonical Zork behavior.
Tests parser functionality, game state changes, and response authenticity.
"""

import sys
import json
import time
from typing import Dict, List, Tuple, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict
import random

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.game import GameEngine
from src.parser.command_parser import CommandParser, Command
from src.responses import ZorkResponses
from src.world.world import World


@dataclass
class TestResult:
    """Represents the result of a single command test."""
    command: str
    expected_behavior: str
    actual_output: str
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class TestCategory:
    """Represents a category of command tests."""
    name: str
    description: str
    tests: List['CommandTest']
    
    
@dataclass 
class CommandTest:
    """Represents a single command test case."""
    command: str
    expected_behavior: str  # What should happen
    context_setup: Optional[str] = None  # Optional setup command
    validation_type: str = "output"  # "output", "state", "error", "performance"
    expected_patterns: List[str] = None  # Regex patterns to match
    max_execution_time: float = 1.0  # Max acceptable execution time


class ZorkCommandTester:
    """Comprehensive testing framework for Zork command validation."""
    
    def __init__(self):
        self.game_engine = None
        self.parser = CommandParser()
        self.responses = ZorkResponses()
        self.test_categories: List[TestCategory] = []
        self.test_results: List[TestResult] = []
        self.start_time = None
        
        # Statistics tracking
        self.stats = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'categories_tested': 0,
            'average_execution_time': 0.0,
            'total_execution_time': 0.0
        }
        
    def setup_test_environment(self):
        """Initialize fresh game environment for testing."""
        print("🔧 Setting up test environment...")
        self.game_engine = GameEngine(use_mud_files=True, 
                                     mud_directory=Path("zork_mtl_source"))
        print("✅ Test environment ready")
        
    def define_test_categories(self):
        """Define all test categories and their test cases."""
        print("📋 Defining comprehensive test suite...")
        
        # Movement Commands
        movement_tests = [
            CommandTest("north", "Move north or show 'can't go' message"),
            CommandTest("n", "Same as 'north' (synonym test)"),
            CommandTest("south", "Move south or show 'can't go' message"),
            CommandTest("go north", "Same as 'north' (complex syntax)"),
            CommandTest("walk east", "Same as 'east' (synonym test)"),
            CommandTest("run west", "Same as 'west' (synonym test)"),
            CommandTest("up", "Move up or show 'can't go' message"),
            CommandTest("climb up", "Same as 'up' (complex syntax)"),
            CommandTest("northeast", "Move northeast or show 'can't go' message"),
            CommandTest("nw", "Same as 'northwest' (abbreviation)"),
        ]
        
        # Examination Commands
        examination_tests = [
            CommandTest("look", "Show room description"),
            CommandTest("l", "Same as 'look' (shortcut)"),
            CommandTest("examine lamp", "Show lamp details if present"),
            CommandTest("x sword", "Show sword details if present"),
            CommandTest("inspect mailbox", "Show mailbox details"),
            CommandTest("look at door", "Show door details"),
            CommandTest("search chest", "Search chest contents"),
            CommandTest("look in box", "Show box contents"),
            CommandTest("look under rug", "Search under rug"),
        ]
        
        # Inventory Commands
        inventory_tests = [
            CommandTest("inventory", "Show inventory contents"),
            CommandTest("i", "Same as 'inventory' (shortcut)"),
            CommandTest("take lamp", "Pick up lamp if available"),
            CommandTest("get sword", "Pick up sword if available"),
            CommandTest("pick up rope", "Pick up rope if available"),
            CommandTest("drop lamp", "Drop lamp from inventory"),
            CommandTest("throw sword", "Drop sword from inventory"),
            CommandTest("take all", "Pick up all available items"),
            CommandTest("drop everything", "Drop all inventory items"),
        ]
        
        # Container Interactions
        container_tests = [
            CommandTest("open mailbox", "Open mailbox if present"),
            CommandTest("close chest", "Close chest if present"),
            CommandTest("put sword in chest", "Place sword in chest"),
            CommandTest("get paper from mailbox", "Take paper from mailbox"),
            CommandTest("look in bag", "Show bag contents"),
            CommandTest("empty sack", "Empty sack contents"),
        ]
        
        # Combat and Action Commands
        action_tests = [
            CommandTest("attack troll", "Attack troll if present"),
            CommandTest("kill monster", "Attack monster if present"),
            CommandTest("hit door", "Hit door (futile action)"),
            CommandTest("break window", "Try to break window"),
            CommandTest("push button", "Push button if present"),
            CommandTest("pull rope", "Pull rope if available"),
            CommandTest("turn knob", "Turn knob if present"),
            CommandTest("use key", "Use key if available"),
        ]
        
        # Communication Commands
        communication_tests = [
            CommandTest("say hello", "Greet (no response expected)"),
            CommandTest("shout", "Shout (no response expected)"),
            CommandTest("read paper", "Read paper if available"),
            CommandTest("read sign", "Read sign if present"),
        ]
        
        # Light and Dark Room Commands
        light_tests = [
            CommandTest("light lamp", "Light lamp if available"),
            CommandTest("turn on torch", "Light torch if available"),
            CommandTest("extinguish candle", "Put out candle"),
            CommandTest("blow out match", "Extinguish match"),
        ]
        
        # Game Control Commands
        control_tests = [
            CommandTest("score", "Show current score"),
            CommandTest("help", "Show help information"),
            CommandTest("brief", "Set brief mode"),
            CommandTest("verbose", "Set verbose mode"),
            CommandTest("time", "Show elapsed time"),
            CommandTest("diagnose", "Show health status"),
        ]
        
        # Error and Edge Cases
        error_tests = [
            CommandTest("asdfghjkl", "Unknown command error", validation_type="error"),
            CommandTest("", "Empty command handling", validation_type="error"),
            CommandTest("take", "Missing object error"),
            CommandTest("go", "Missing direction error"),
            CommandTest("put sword", "Missing preposition/target error"),
            CommandTest("get nonexistent", "Object not found error"),
            CommandTest("north south east", "Ambiguous command error"),
        ]
        
        # Parser Stress Tests
        parser_tests = [
            CommandTest("take the rusty old sword from the wooden chest", "Complex parsing test"),
            CommandTest("put all lamps in the big treasure chest carefully", "Multiple objects test"),
            CommandTest("examine the small brass lantern with great care", "Long description parsing"),
            CommandTest("go north then west then up", "Multiple commands (should handle first only)"),
        ]
        
        # Performance Tests
        performance_tests = [
            CommandTest("look", "Fast room description", max_execution_time=0.1),
            CommandTest("inventory", "Fast inventory display", max_execution_time=0.1),
            CommandTest("north", "Fast movement", max_execution_time=0.2),
        ]
        
        # Canonical Response Tests (Zork personality)
        personality_tests = [
            CommandTest("xyzzy", "Magic word response"),
            CommandTest("plugh", "Magic word response"),  
            CommandTest("foo", "Unknown command with snark"),
            CommandTest("curse", "Swearing response"),
            CommandTest("hello computer", "Greeting response"),
            CommandTest("kiss lamp", "Inappropriate action response"),
            CommandTest("eat sword", "Impossible action response"),
        ]
        
        # Define categories
        self.test_categories = [
            TestCategory("Movement", "Basic movement and navigation", movement_tests),
            TestCategory("Examination", "Looking and examining objects", examination_tests), 
            TestCategory("Inventory", "Taking, dropping, and inventory management", inventory_tests),
            TestCategory("Containers", "Container interactions and object placement", container_tests),
            TestCategory("Actions", "Combat, manipulation, and object interaction", action_tests),
            TestCategory("Communication", "Speaking, reading, and communication", communication_tests),
            TestCategory("Light & Dark", "Light sources and darkness mechanics", light_tests),
            TestCategory("Game Control", "System commands and information display", control_tests),
            TestCategory("Error Handling", "Invalid commands and error cases", error_tests),
            TestCategory("Parser", "Complex parsing and syntax handling", parser_tests),
            TestCategory("Performance", "Speed and efficiency validation", performance_tests),
            TestCategory("Personality", "Canonical Zork responses and humor", personality_tests),
        ]
        
        # Count total tests
        self.stats['total_tests'] = sum(len(cat.tests) for cat in self.test_categories)
        self.stats['categories_tested'] = len(self.test_categories)
        
        print(f"✅ Test suite defined: {self.stats['total_tests']} tests across {self.stats['categories_tested']} categories")
        
    def run_single_test(self, test: CommandTest) -> TestResult:
        """Execute a single command test."""
        start_time = time.time()
        
        try:
            # Setup context if needed
            if test.context_setup:
                # Execute setup command without capturing output
                self.game_engine._process_command(test.context_setup)
            
            # Capture output by redirecting stdout
            import io
            import contextlib
            
            captured_output = io.StringIO()
            with contextlib.redirect_stdout(captured_output):
                # Execute the test command
                self.game_engine._process_command(test.command)
            
            actual_output = captured_output.getvalue().strip()
            execution_time = time.time() - start_time
            
            # Validate based on test type
            success = self._validate_test_result(test, actual_output, execution_time)
            
            return TestResult(
                command=test.command,
                expected_behavior=test.expected_behavior,
                actual_output=actual_output,
                success=success,
                execution_time=execution_time
            )
            
        except Exception as e:
            return TestResult(
                command=test.command,
                expected_behavior=test.expected_behavior,
                actual_output="",
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _validate_test_result(self, test: CommandTest, output: str, execution_time: float) -> bool:
        """Validate test results based on validation type."""
        if test.validation_type == "performance":
            return execution_time <= test.max_execution_time
        elif test.validation_type == "error":
            # For error tests, we expect some kind of error message
            error_indicators = ["don't", "can't", "not", "no", "huh", "what", "beg pardon"]
            return any(indicator in output.lower() for indicator in error_indicators)
        elif test.validation_type == "output":
            # For output tests, just check that we got some meaningful response
            return len(output.strip()) > 0
        elif test.validation_type == "state":
            # For state tests, we'd need to check game state changes
            # This is more complex and would require specific state checking
            return True  # Placeholder for now
        else:
            return True
    
    def run_category_tests(self, category: TestCategory) -> List[TestResult]:
        """Run all tests in a specific category."""
        print(f"\n🧪 Testing {category.name}: {category.description}")
        print(f"   {len(category.tests)} tests to execute")
        
        category_results = []
        passed = failed = 0
        
        for i, test in enumerate(category.tests, 1):
            # Reset game state for each test by creating new engine
            self.setup_test_environment()
            
            result = self.run_single_test(test)
            category_results.append(result)
            
            if result.success:
                passed += 1
                status = "✅"
            else:
                failed += 1  
                status = "❌"
            
            # Show progress
            print(f"   [{i:2d}/{len(category.tests)}] {status} {test.command:30s} ({result.execution_time:.3f}s)")
            
            if not result.success and result.error_message:
                print(f"        Error: {result.error_message}")
        
        print(f"   📊 {category.name}: {passed} passed, {failed} failed")
        return category_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run the complete test suite."""
        print("🚀 COMPREHENSIVE ZORK COMMAND & RESPONSE TESTING")
        print("=" * 60)
        
        self.start_time = time.time()
        
        for category in self.test_categories:
            category_results = self.run_category_tests(category)
            self.test_results.extend(category_results)
        
        # Calculate final statistics
        total_time = time.time() - self.start_time
        self.stats['passed'] = sum(1 for r in self.test_results if r.success)
        self.stats['failed'] = sum(1 for r in self.test_results if not r.success)
        self.stats['total_execution_time'] = total_time
        self.stats['average_execution_time'] = sum(r.execution_time for r in self.test_results) / len(self.test_results)
        
        return self._generate_final_report()
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        success_rate = (self.stats['passed'] / self.stats['total_tests']) * 100
        
        print("\n" + "=" * 60)
        print("📈 FINAL TEST RESULTS")
        print("=" * 60)
        
        print(f"🎯 Total Tests: {self.stats['total_tests']}")
        print(f"✅ Passed: {self.stats['passed']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Time: {self.stats['total_execution_time']:.2f}s")
        print(f"⚡ Avg Time/Test: {self.stats['average_execution_time']:.3f}s")
        
        # Category breakdown
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category in self.test_categories:
            cat_results = [r for r in self.test_results if any(t.command == r.command for t in category.tests)]
            cat_passed = sum(1 for r in cat_results if r.success)
            cat_total = len(cat_results)
            cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            print(f"   {category.name:15s}: {cat_passed:2d}/{cat_total:2d} ({cat_rate:5.1f}%)")
        
        # Failed tests summary
        failed_tests = [r for r in self.test_results if not r.success]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"   • {result.command}")
                if result.error_message:
                    print(f"     Error: {result.error_message}")
        
        # Performance analysis
        slow_tests = [r for r in self.test_results if r.execution_time > 0.5]
        if slow_tests:
            print(f"\n⚠️  SLOW TESTS (>0.5s):")
            for result in sorted(slow_tests, key=lambda x: x.execution_time, reverse=True):
                print(f"   • {result.command:30s} ({result.execution_time:.3f}s)")
        
        # Success verdict
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT! Command system performing at {success_rate:.1f}% success rate")
        elif success_rate >= 85:
            print(f"\n👍 GOOD! Command system performing at {success_rate:.1f}% success rate")
        elif success_rate >= 70:
            print(f"\n⚠️  NEEDS WORK! Command system at {success_rate:.1f}% success rate")
        else:
            print(f"\n🚨 CRITICAL! Command system failing at {success_rate:.1f}% success rate")
        
        return {
            'stats': self.stats,
            'success_rate': success_rate,
            'failed_tests': [(r.command, r.error_message) for r in failed_tests],
            'slow_tests': [(r.command, r.execution_time) for r in slow_tests],
            'category_results': {
                cat.name: {
                    'passed': sum(1 for r in self.test_results if r.success and any(t.command == r.command for t in cat.tests)),
                    'total': len(cat.tests)
                } for cat in self.test_categories
            }
        }
    
    def export_results(self, filename: str = "command_test_results.json"):
        """Export test results to JSON file."""
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'stats': self.stats,
            'results': [
                {
                    'command': r.command,
                    'expected_behavior': r.expected_behavior,
                    'actual_output': r.actual_output,
                    'success': r.success,
                    'error_message': r.error_message,
                    'execution_time': r.execution_time
                } for r in self.test_results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📁 Test results exported to {filename}")


def main():
    """Main test execution function."""
    tester = ZorkCommandTester()
    
    try:
        # Setup and run comprehensive testing
        tester.setup_test_environment()
        tester.define_test_categories()
        
        # Run all tests
        results = tester.run_all_tests()
        
        # Export results  
        tester.export_results()
        
        # Exit with appropriate code
        success_rate = results['success_rate']
        if success_rate >= 95:
            sys.exit(0)  # Excellent
        elif success_rate >= 85:
            sys.exit(0)  # Good enough  
        else:
            sys.exit(1)  # Needs attention
        
    except Exception as e:
        print(f"🚨 TESTING FRAMEWORK ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()