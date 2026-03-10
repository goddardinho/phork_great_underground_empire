#!/usr/bin/env python3
"""
Quick Connectivity Validation
Fast validation of world connectivity for development workflow
"""

import sys
from pathlib import Path
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game import GameEngine
from collections import deque


def quick_connectivity_check(start_room: str = "WHOUS") -> bool:
    """
    Quick connectivity check - fast BFS to validate basic reachability.
    Returns True if connectivity is good (>80% rooms reachable).
    """
    
    print("⚡ Quick Connectivity Check...")
    
    game = GameEngine(use_mud_files=True)
    if not game.world.rooms:
        print("❌ No rooms loaded!")
        return False
    
    total_rooms = len(game.world.rooms)
    visited = set()
    queue = deque([start_room])
    
    start_time = time.time()
    
    # BFS traversal
    while queue:
        room_id = queue.popleft()
        
        if room_id in visited:
            continue
            
        room = game.world.get_room(room_id)
        if not room:
            continue
            
        visited.add(room_id)
        
        # Add connected rooms
        for target in room.exits.values():
            if target not in visited and target in game.world.rooms:
                queue.append(target)
    
    elapsed = time.time() - start_time
    reachable = len(visited)
    percentage = (reachable / total_rooms) * 100
    
    # Results
    print(f"   📊 {reachable}/{total_rooms} rooms reachable ({percentage:.1f}%)")
    print(f"   ⏱️  {elapsed:.3f} seconds")
    
    if percentage >= 90:
        print(f"   ✅ EXCELLENT connectivity")
        return True
    elif percentage >= 80:
        print(f"   ⚠️  GOOD connectivity")
        return True  
    else:
        print(f"   ❌ POOR connectivity - needs improvement")
        return False


def validate_key_locations() -> bool:
    """Validate that key game locations are reachable from start."""
    
    print("\n🗝️  Validating Key Locations...")
    
    game = GameEngine(use_mud_files=True)
    key_rooms = [
        ("WHOUS", "West of House (Start)"),
        ("NHOUS", "North of House"), 
        ("EHOUS", "Behind House"),
        ("KITCH", "Kitchen"),
        ("LROOM", "Living Room"),
        ("CELLA", "Cellar"),
        ("TREAS", "Treasure Room"),
        ("MTREE", "Up a Tree"),
        ("CLEAR", "Forest Clearing"),
    ]
    
    # BFS from West of House
    visited = set()
    queue = deque(["WHOUS"])
    
    while queue:
        room_id = queue.popleft()
        
        if room_id in visited:
            continue
            
        room = game.world.get_room(room_id)
        if not room:
            continue
            
        visited.add(room_id)
        
        for target in room.exits.values():
            if target not in visited and target in game.world.rooms:
                queue.append(target)
    
    # Check key locations
    all_reachable = True
    for room_id, description in key_rooms:
        if room_id in visited:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - NOT REACHABLE")
            all_reachable = False
    
    return all_reachable


def check_exit_integrity() -> bool:
    """Quick check for broken exits."""
    
    print("\n🚪 Checking Exit Integrity...")
    
    game = GameEngine(use_mud_files=True)
    broken_count = 0
    total_count = 0
    
    for room in game.world.rooms.values():
        for direction, target in room.exits.items():
            total_count += 1
            if target not in game.world.rooms:
                broken_count += 1
    
    success_rate = ((total_count - broken_count) / total_count) * 100 if total_count > 0 else 0
    
    print(f"   📊 {total_count - broken_count}/{total_count} exits working ({success_rate:.1f}%)")
    
    if broken_count > 0:
        print(f"   ⚠️  {broken_count} broken exits found")
    
    return broken_count == 0


def main():
    """Run quick connectivity validation."""
    
    print("🔍 QUICK CONNECTIVITY VALIDATION")
    print("=" * 40)
    
    start_time = time.time()
    
    # Run checks
    connectivity_good = quick_connectivity_check()
    key_locations_ok = validate_key_locations() 
    exits_intact = check_exit_integrity()
    
    total_time = time.time() - start_time
    
    # Summary
    print(f"\n📋 VALIDATION SUMMARY")
    print(f"   Overall Time: {total_time:.3f}s")
    
    if connectivity_good and key_locations_ok and exits_intact:
        print(f"   🎉 ALL CHECKS PASSED - World connectivity is excellent!")
        return True
    else:
        print(f"   ⚠️  ISSUES FOUND - Run full connectivity test for details")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)