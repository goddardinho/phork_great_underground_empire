#!/usr/bin/env python3
"""
Integration test for recent fixes: room descriptions and object recognition
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.game import GameEngine
from pathlib import Path

def test_room_descriptions():
    """Test that canonical room descriptions are working."""
    print("🏠 Testing Room Descriptions...")
    
    game = GameEngine(use_mud_files=True, mud_directory=Path('zork_mtl_source'))
    
    # Test EHOUS (Behind House) - should have window description
    ehous = game.world.get_room('EHOUS')
    if ehous:
        print(f"✓ EHOUS found: {ehous.name}")
        if 'slightly ajar' in ehous.description:
            print("✓ EHOUS has proper window description")
        else:
            print(f"✗ EHOUS description: {ehous.description}")
            return False
    else:
        print("✗ EHOUS room not found")
        return False
    
    # Test KITCH (Kitchen) - should have canonical description
    kitch = game.world.get_room('KITCH')
    if kitch and 'preparation of food' in kitch.description:
        print("✓ KITCH has canonical description")
    else:
        print(f"✗ KITCH description: {kitch.description if kitch else 'Not found'}")
        return False
    
    # Test LROOM (Living Room) - should have cyclops hole description
    lroom = game.world.get_room('LROOM')
    if lroom and 'cyclops-shaped hole' in lroom.description:
        print("✓ LROOM has canonical description")
    else:
        print(f"✗ LROOM description: {lroom.description if lroom else 'Not found'}")
        return False
    
    return True

def test_object_recognition():
    """Test that objects are properly loaded and recognized."""
    print("🪟 Testing Object Recognition...")
    
    game = GameEngine(use_mud_files=True, mud_directory=Path('zork_mtl_source'))
    
    # Check if WINDO object exists
    if hasattr(game, 'object_manager'):
        windo = game.object_manager.get_object('WINDO')
    else:
        # Fallback for older structure
        windo = getattr(game, 'objects', {}).get('WINDO')
    
    if windo:
        print("✓ WINDO object found")
        print(f"  Name: {windo.name}")
        print(f"  Description: {windo.description[:50]}...")
        if windo.get_attribute('openable', False):
            print("✓ WINDO is openable")
        else:
            print("✗ WINDO not openable")
            return False
    else:
        print("✗ WINDO object not found")
        return False
    
    # Check EHOUS has window object
    ehous = game.world.get_room('EHOUS')
    if ehous and 'WINDO' in ehous.items:
        print("✓ EHOUS contains WINDO object")
    else:
        print(f"✗ EHOUS items: {ehous.items if ehous else 'Room not found'}")
        return False
    
    return True

def test_display_format():
    """Test that room descriptions don't show redundant names."""
    print("🖼️ Testing Display Format...")
    
    game = GameEngine(use_mud_files=True, mud_directory=Path('zork_mtl_source'))
    
    ehous = game.world.get_room('EHOUS')
    if ehous:
        # Test with name excluded
        desc_no_name = ehous.get_description(force_verbose=True, include_name=False)
        if not desc_no_name.startswith('Behind House'):
            print("✓ Description excludes room name when requested")
        else:
            print("✗ Description still includes room name")
            return False
        
        # Test with name included  
        desc_with_name = ehous.get_description(force_verbose=True, include_name=True)
        if desc_with_name.startswith('Behind House'):
            print("✓ Description includes room name when requested")
        else:
            print("✗ Description doesn't include room name when requested")
            return False
    else:
        print("✗ EHOUS room not found")
        return False
    
    return True

def test_connectivity():
    """Test basic room connectivity still works."""
    print("🗺️ Testing Room Connectivity...")
    
    game = GameEngine(use_mud_files=True, mud_directory=Path('zork_mtl_source'))
    
    # Test house perimeter navigation
    whous = game.world.get_room('WHOUS')
    if whous and 'north' in whous.exits:
        nhous_id = whous.exits['north']
        if nhous_id == 'NHOUS':
            print("✓ WHOUS → NHOUS connection")
        else:
            print(f"✗ WHOUS north leads to {nhous_id}, expected NHOUS")
            return False
    else:
        print("✗ WHOUS or north exit not found")
        return False
    
    # Test kitchen window connection
    ehous = game.world.get_room('EHOUS')
    if ehous and 'west' in ehous.exits:
        kitch_id = ehous.exits.get('west') or ehous.exits.get('enter')
        if 'KITCH' in str(kitch_id):  # Might be KITCHEN-WINDOW door
            print("✓ EHOUS → KITCH connection")
        else:
            print(f"✗ EHOUS west/enter leads to {kitch_id}")
            return False
    else:
        print("✗ EHOUS or west exit not found")
        return False
    
    return True

def run_all_tests():
    """Run all integration tests."""
    print("🧪 Running Integration Tests for Recent Fixes")
    print("=" * 50)
    
    tests = [
        test_room_descriptions,
        test_object_recognition,
        test_display_format,
        test_connectivity
    ]
    
    total_tests = len(tests)
    passed_tests = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed_tests += 1
                print()
        except Exception as e:
            print(f"✗ {test_func.__name__} failed with error: {e}")
            print()
    
    print("=" * 50)
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)