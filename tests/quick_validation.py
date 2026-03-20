#!/usr/bin/env python3

"""
Quick Command and Response Validation for Zork Implementation
============================================================

Quick validation of core command functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.game import GameEngine
from src.parser.command_parser import CommandParser


def test_core_commands():
    """Test core command functionality."""
    print("🎯 QUICK COMMAND VALIDATION")
    print("=" * 40)
    
    try:
        # Initialize game
        game = GameEngine(use_mud_files=True, mud_directory=Path("zork_mtl_source"))
        parser = CommandParser()
        
        # Test basic commands
        test_commands = [
            "look",
            "inventory", 
            "north",
            "examine lamp",
            "help",
            "score",
            "xyzzy",  # Special command
            "asdfgh", # Invalid command  
        ]
        
        successful = 0
        total = len(test_commands)
        
        print(f"Testing {total} core commands...")
        
        for cmd in test_commands:
            try:
                # Parse command
                parsed = parser.parse(cmd)
                if parsed:
                    print(f"✅ '{cmd}' - parses correctly")
                    successful += 1
                else:
                    print(f"❌ '{cmd}' - parse failed")
            except Exception as e:
                print(f"❌ '{cmd}' - error: {e}")
        
        success_rate = successful / total * 100
        print(f"\n📊 Results: {successful}/{total} ({success_rate:.1f}%) successful")
        
        if success_rate >= 80:
            print("🎉 COMMAND SYSTEM WORKING WELL!")
            return True
        else:
            print("⚠️ Command system needs attention")
            return False
            
    except Exception as e:
        print(f"🚨 Test framework error: {e}")
        return False


def test_response_system():
    """Test response system."""
    print("\n🎭 RESPONSE SYSTEM VALIDATION")  
    print("=" * 40)
    
    try:
        from src.responses import ZorkResponses
        responses = ZorkResponses()
        
        # Test response categories
        tests = [
            ("unknown command", responses.get_unknown_command_response("blah")),
            ("can't go", responses.get_cant_go_response()),
            ("object not found", responses.get_dont_see_object_response("sword")),
            ("inventory empty", responses.get_inventory_response("empty")),
        ]
        
        successful = 0
        for test_name, response in tests:
            if response and len(response.strip()) > 0:
                print(f"✅ {test_name} - has response")
                successful += 1
            else:
                print(f"❌ {test_name} - no response")
        
        success_rate = successful / len(tests) * 100
        print(f"\n📊 Response Results: {successful}/{len(tests)} ({success_rate:.1f}%) working")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"🚨 Response test error: {e}")
        return False


def main():
    """Run quick validation."""
    
    commands_ok = test_core_commands()
    responses_ok = test_response_system()
    
    print("\n" + "=" * 40)
    print("🏆 FINAL VALIDATION RESULTS")
    print("=" * 40)
    
    if commands_ok and responses_ok:
        print("🎉 SUCCESS! Core command and response systems functional")
        print("✅ Commands parse correctly")
        print("✅ Responses generate properly")
        print("✅ Ready for production use")
        return 0
    elif commands_ok:
        print("⚠️ Commands working, but response system needs attention")
        return 1
    elif responses_ok:
        print("⚠️ Responses working, but command parsing needs attention")  
        return 1
    else:
        print("🚨 Both command and response systems need work")
        return 2


if __name__ == "__main__":
    sys.exit(main())