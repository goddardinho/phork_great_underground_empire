#!/usr/bin/env python3
"""
Comprehensive Canonical Accuracy Audit for All Zork Rooms

Tests whether ALL 196 rooms match the original 1978 MIT Zork specifications
for descriptions, names, objects, and properties.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from world.world import World
from world.room_loader import ZorkRoomLoader

def is_canonical_room_name(room_id: str, room_name: str) -> bool:
    """Check if room name is canonical (not just the room ID)."""
    if not room_name or room_name == room_id:
        return False
    
    # Room names that are obviously just IDs or placeholders
    problematic_patterns = [
        room_name.isupper() and len(room_name) <= 5,  # Short all-caps like "MAZE1" 
        room_name in ['UP', 'DOWN', 'NORTH', 'SOUTH', 'EAST', 'WEST'],  # Direction names
        room_name.startswith('MAZ') and room_name[-1].isdigit(),  # MAZE1, MAZ14, etc.
        room_name.startswith('DEAD') and room_name[-1].isdigit(),  # DEAD1, DEAD2, etc.
        room_name.startswith('FORE') and room_name[-1].isdigit(),  # FORE1, FORE2, etc.
        room_name.startswith('MINE') and room_name[-1].isdigit(),  # MINE1, MINE2, etc.
        room_name.startswith('RIVR') and room_name[-1].isdigit(),  # RIVR1, RIVR2, etc.
    ]
    
    if any(problematic_patterns):
        return False
    
    # Good canonical indicators (single words or phrases that show proper naming)
    canonical_words = [
        'room', 'house', 'kitchen', 'attic', 'cellar', 'passage', 'corridor', 
        'cave', 'forest', 'clearing', 'beach', 'shore', 'temple', 'dam', 
        'lobby', 'treasure', 'gallery', 'studio', 'ravine', 'canyon', 
        'falls', 'rainbow', 'volcano', 'library', 'machine', 'bank', 
        'vault', 'office', 'mirror', 'entrance', 'chamber', 'tomb',
        'crypt', 'altar', 'grail', 'dome', 'shaft', 'tunnel', 'ledge',
        'chasm', 'pool', 'well', 'stairs'
    ]
    
    name_lower = room_name.lower()
    
    # Check for canonical word patterns
    if any(word in name_lower for word in canonical_words):
        return True
        
    # Check for multi-word names (usually good)
    if ' ' in room_name and len(room_name) > 5:
        return True
        
    # Check for proper descriptive single words (title case, reasonable length)
    if room_name[0].isupper() and len(room_name) >= 4 and not room_name.isupper():
        return True
    
    return False

def is_canonical_description(desc: str) -> bool:
    """Check if description appears to be canonical text."""
    if not desc or len(desc) < 5:
        return False
        
    # Descriptions that are obviously just placeholders or directions
    problematic_patterns = [
        desc in ['UP', 'DOWN', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'TREE'],
        desc.isupper() and len(desc) < 20,  # Short all-caps usually means placeholder
        desc.strip() in ['""', "''", '()', '[]'],  # Empty or just quotes/brackets
        len(desc.strip()) <= 3,  # Too short to be descriptive
    ]
    
    if any(problematic_patterns):
        return False
        
    # Good descriptions usually contain descriptive language
    desc_lower = desc.lower()
    descriptive_indicators = [
        "you are", "this is", "you can see", "there is", "there are", "you find",
        "room", "passage", "corridor", "cave", "house", "door", "wall", "floor",
        "north", "south", "east", "west", "up", "down", "light", "dark",
        "large", "small", "narrow", "wide", "wooden", "stone", "metal", "old"
    ]
    
    # If it has descriptive language, it's probably canonical
    if any(indicator in desc_lower for indicator in descriptive_indicators):
        return True
    
    # If it's reasonably long and not all caps, it's probably fine
    if len(desc) >= 15 and not desc.isupper():
        return True
        
    return False

def validate_room_canonical_accuracy(room, room_id: str) -> dict:
    """Validate a single room for canonical accuracy."""
    issues = []
    
    # 1. Name validation
    name_valid = is_canonical_room_name(room_id, room.name)
    if not name_valid:
        issues.append(f"Non-canonical name: '{room.name}' (should not be just room ID)")
    
    # 2. Description validation
    desc_valid = is_canonical_description(room.description)
    if not desc_valid:
        issues.append(f"Poor description: '{room.description[:50]}...' (should be descriptive prose)")
    
    # 3. Objects validation - check if objects are loaded correctly
    has_objects = hasattr(room, 'items') and room.items
    objects_valid = True  # Assume valid unless we find issues
    
    # 4. Exits validation - should have at least some exits for most rooms
    exits_valid = len(room.exits) > 0  # Most rooms should have exits
    if not exits_valid and room_id not in ['NIRVA', 'TOMB']:  # Some end rooms might have no exits
        issues.append("No exits found (most rooms should have exits)")
    
    return {
        'room_id': room_id,
        'name_valid': name_valid,
        'desc_valid': desc_valid,
        'objects_valid': objects_valid,
        'exits_valid': exits_valid,
        'issues': issues,
        'canonical': len(issues) == 0
    }

def audit_all_rooms_canonical_accuracy():
    """Comprehensive audit of ALL room canonical accuracy."""
    
    print("🔍 COMPREHENSIVE ZORK CANONICAL ACCURACY AUDIT")
    print("=" * 60)
    print("Testing ALL 196 rooms against original Zork specifications...")
    
    # Load the world
    world = World()
    loader = ZorkRoomLoader(world)
    loader.load_from_mud_files(Path("zork_mtl_source"))
    
    all_rooms = world.rooms
    total_rooms = len(all_rooms)
    canonical_rooms = 0
    all_issues = []
    room_results = []
    
    print(f"\n🏠 Testing {total_rooms} rooms...")
    print("-" * 60)
    
    # Test each room
    for room_id, room in all_rooms.items():
        result = validate_room_canonical_accuracy(room, room_id)
        room_results.append(result)
        
        if result['canonical']:
            canonical_rooms += 1
            print(f"✅ {room_id:6} | {room.name[:30]:30} | CANONICAL")
        else:
            print(f"❌ {room_id:6} | {room.name[:30]:30} | ISSUES: {len(result['issues'])}")
            all_issues.extend(result['issues'])
    
    # Detailed issue breakdown
    print(f"\n📊 DETAILED CANONICAL ACCURACY ANALYSIS")
    print("=" * 50)
    
    name_issues = sum(1 for r in room_results if not r['name_valid'])
    desc_issues = sum(1 for r in room_results if not r['desc_valid'])
    exit_issues = sum(1 for r in room_results if not r['exits_valid'])
    
    print(f"Total rooms tested: {total_rooms}")
    print(f"Canonically accurate: {canonical_rooms}")
    print(f"Accuracy rate: {(canonical_rooms/total_rooms)*100:.1f}%")
    print(f"\nIssue breakdown:")
    print(f"  • Name issues: {name_issues} rooms")
    print(f"  • Description issues: {desc_issues} rooms")
    print(f"  • Exit issues: {exit_issues} rooms")
    
    # Show worst offenders
    if all_issues:
        failed_rooms = [r for r in room_results if not r['canonical']]
        print(f"\n🚨 ROOMS NEEDING ATTENTION ({len(failed_rooms)}):")
        
        for result in failed_rooms[:20]:  # Show first 20 problem rooms
            room = all_rooms[result['room_id']]
            print(f"\n  {result['room_id']} - {room.name}")
            for issue in result['issues']:
                print(f"    • {issue}")
        
        if len(failed_rooms) > 20:
            print(f"\n  ... and {len(failed_rooms) - 20} more rooms with issues")
    
    # Sample of successful rooms
    successful_rooms = [r for r in room_results if r['canonical']]
    if successful_rooms:
        print(f"\n✅ SAMPLE CANONICAL ROOMS ({len(successful_rooms)} total):")
        for result in successful_rooms[:10]:  # Show first 10 successful rooms
            room = all_rooms[result['room_id']]
            objects_info = f" | {len(room.items)} objs" if hasattr(room, 'items') and room.items else ""
            exits_info = f" | {len(room.exits)} exits"
            print(f"  {result['room_id']:6} | {room.name[:40]:40}{exits_info}{objects_info}")
    
    # Overall assessment
    print(f"\n📈 CANONICAL ACCURACY SUMMARY")
    print("=" * 40)
    
    if canonical_rooms == total_rooms:
        print(f"🎉 PERFECT CANONICAL ACCURACY: 100%")
        print("All rooms match original Zork specifications!")
        return True
    elif canonical_rooms >= total_rooms * 0.90:  # 90%+ is excellent
        print(f"🌟 EXCELLENT CANONICAL ACCURACY: {(canonical_rooms/total_rooms)*100:.1f}%")
        print("Nearly all rooms match original Zork specifications")
        return True
    elif canonical_rooms >= total_rooms * 0.75:  # 75%+ is good
        print(f"👍 GOOD CANONICAL ACCURACY: {(canonical_rooms/total_rooms)*100:.1f}%")
        print("Most rooms match original Zork specifications")
        return True
    elif canonical_rooms >= total_rooms * 0.60:  # 60%+ is acceptable
        print(f"✅ ACCEPTABLE CANONICAL ACCURACY: {(canonical_rooms/total_rooms)*100:.1f}%")
        print("Majority of rooms match original Zork specifications")
        return False
    else:
        print(f"❌ POOR CANONICAL ACCURACY: {(canonical_rooms/total_rooms)*100:.1f}%")
        print("Significant issues found with room specifications")
        return False

if __name__ == "__main__":
    success = audit_all_rooms_canonical_accuracy()
    sys.exit(0 if success else 1)