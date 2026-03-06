#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game import GameEngine

def quick_validate():
    print("🔍 Quick Zork World Validation")
    print("=" * 40)
    
    # Initialize game
    print("Initializing game...")
    game = GameEngine(use_mud_files=True)
    
    # 1. Check starting location
    print(f"\n✅ Starting Location:")
    expected = "WHOUS"
    actual = game.player.current_room
    print(f"   Expected: {expected}")
    print(f"   Actual: {actual}")
    print(f"   Status: {'✅ PASS' if actual == expected else '❌ FAIL'}")
    
    # 2. Check key room existence
    print(f"\n✅ Key Rooms:")
    key_rooms = {
        "WHOUS": "West of House",
        "NHOUS": "North of House", 
        "SHOUS": "South of House",
        "EHOUS": "Behind House",
        "LROOM": "Living Room",
        "KITCH": "Kitchen", 
        "ATTIC": "Attic",
        "CELLA": "Cellar"
    }
    
    missing_rooms = []
    for room_id, expected_name in key_rooms.items():
        room = game.world.get_room(room_id)
        if room:
            print(f"   {room_id}: ✅ '{room.name}' (exits: {len(room.exits)}, items: {len(room.items)})")
        else:
            print(f"   {room_id}: ❌ MISSING")
            missing_rooms.append(room_id)
    
    # 3. Check key exit connections
    print(f"\n✅ Critical Connections:")
    critical_exits = {
        ("WHOUS", "north"): "NHOUS",
        ("WHOUS", "south"): "SHOUS", 
        # Note: WHOUS east is intentionally blocked (locked front door)
        ("LROOM", "down"): "CELLA",
        ("CELLA", "up"): "LROOM",
    }
    
    exit_failures = []
    for (room_id, direction), expected_target in critical_exits.items():
        room = game.world.get_room(room_id)
        if room and direction in room.exits:
            actual_target = room.exits[direction]
            if actual_target == expected_target:
                print(f"   {room_id} {direction} -> {actual_target}: ✅")
            else:
                print(f"   {room_id} {direction} -> {actual_target}: ❌ (expected {expected_target})")
                exit_failures.append((room_id, direction, expected_target, actual_target))
        else:
            print(f"   {room_id} {direction}: ❌ EXIT MISSING")
            exit_failures.append((room_id, direction, expected_target, "MISSING"))
    
    # 4. Check room descriptions
    print(f"\n✅ Room Descriptions:")
    description_checks = {
        "WHOUS": ["open field", "west of", "white house"],
        "LROOM": ["living room"],
        "KITCH": ["kitchen"],
        "CELLA": ["cellar"]
    }
    
    description_failures = []
    for room_id, keywords in description_checks.items():
        room = game.world.get_room(room_id)
        if room:
            desc = room.description.lower()
            missing_keywords = [kw for kw in keywords if kw not in desc]
            if missing_keywords:
                print(f"   {room_id}: ❌ Missing keywords: {missing_keywords}")
                description_failures.append((room_id, missing_keywords))
            else:
                print(f"   {room_id}: ✅ Contains expected keywords")
        else:
            print(f"   {room_id}: ❌ ROOM MISSING")
    
    # 5. Summary
    print(f"\n📊 SUMMARY:")
    print(f"   Total rooms loaded: {len(game.world.rooms)}")
    print(f"   Missing key rooms: {len(missing_rooms)}")
    print(f"   Connection failures: {len(exit_failures)}")
    print(f"   Description issues: {len(description_failures)}")
    
    overall_status = "PASS" if (len(missing_rooms) == 0 and 
                               len(exit_failures) == 0 and 
                               actual == expected) else "FAIL"
    print(f"   Overall Status: {'🟢 ' + overall_status if overall_status == 'PASS' else '🔴 ' + overall_status}")
    
    if overall_status == "FAIL":
        print(f"\n❌ Issues Found:")
        if missing_rooms:
            print(f"   Missing rooms: {missing_rooms}")
        if exit_failures:
            print(f"   Exit failures: {exit_failures}")
        if description_failures:
            print(f"   Description failures: {description_failures}")

if __name__ == "__main__":
    quick_validate()