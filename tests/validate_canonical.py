#!/usr/bin/env python3
"""
Canonical validation script for Zork implementation.
Systematically checks rooms and objects against original Zork specifications.
"""

from src.game import GameEngine
from pathlib import Path

def validate_room_objects(game):
    """Validate objects in key rooms match canonical expectations."""
    
    print("🔍 CANONICAL VALIDATION REPORT")
    print("=" * 50)
    
    # Define canonical object expectations
    canonical_rooms = {
        "WHOUS": {
            "description": "West of House", 
            "expected_objects": [],  # Usually empty
            "notes": "Should have boarded front door (non-interactive)"
        },
        "SHOUS": {
            "description": "South of House",
            "expected_objects": ["MAILBOX"],
            "notes": "Mailbox should contain leaflet"
        },
        "EHOUS": {
            "description": "Behind House", 
            "expected_objects": ["WINDO"],
            "notes": "Window should be slightly ajar (open)"
        },
        "LROOM": {
            "description": "Living Room",
            "expected_objects": ["TCASE", "RUG", "SWORD", "LAMP"],
            "notes": "Trophy case, rug, sword, brass lamp all canonical"
        },
        "KITCH": {
            "description": "Kitchen",
            "expected_objects": ["BOTTL", "SBAG"],
            "notes": "Bottle and sack should be present"
        },
        "MGRAT": {
            "description": "Grating Room",
            "expected_objects": ["GRATE"],
            "notes": "Grate should be present and locked initially"
        },
        "TREE": {
            "description": "Up a Tree", 
            "expected_objects": ["NEST", "TTREE"],
            "notes": "Nest should be open with egg inside"
        }
    }
    
    missing_objects = []
    
    for room_id, expectations in canonical_rooms.items():
        room = game.world.get_room(room_id)
        if not room:
            print(f"❌ ROOM NOT FOUND: {room_id}")
            continue
            
        print(f"\n📍 {room_id} ({expectations['description']})")
        print(f"   Current items: {room.items}")
        
        for expected_obj in expectations["expected_objects"]:
            if expected_obj in room.items:
                obj = game.objects.get(expected_obj)
                if obj:
                    print(f"   ✅ {expected_obj}: {obj.name}")
                    # Check object state if it's a container
                    if obj.is_container():
                        state = "open" if obj.is_open() else "closed"
                        contents = obj.get_contents()
                        print(f"      State: {state}, Contents: {contents}")
                else:
                    print(f"   ⚠️  {expected_obj}: Object exists in room but not in game.objects")
            else:
                print(f"   ❌ MISSING: {expected_obj}")
                missing_objects.append((room_id, expected_obj))
        
        print(f"   📝 Notes: {expectations['notes']}")
    
    return missing_objects

def validate_object_states(game):
    """Check critical object states for canonical accuracy."""
    
    print(f"\n🔧 OBJECT STATE VALIDATION")
    print("=" * 30)
    
    critical_objects = {
        "MAILBOX": {"should_be_open": False, "should_contain": ["LEAFLET"]},
        "WINDO": {"should_be_open": True, "notes": "Window starts slightly ajar"},
        "NEST": {"should_be_open": True, "should_contain": ["EGG"]},
        "EGG": {"should_be_open": False, "treasure": True},
        "TORCH": {"lit": False, "light_source": True},
    }
    
    for obj_id, expectations in critical_objects.items():
        obj = game.objects.get(obj_id)
        if not obj:
            print(f"❌ OBJECT NOT FOUND: {obj_id}")
            continue
            
        print(f"\n🔍 {obj_id} ({obj.name})")
        
        # Check container state
        if obj.is_container():
            is_open = obj.is_open()
            expected_open = expectations.get("should_be_open")
            if expected_open is not None:
                status = "✅" if is_open == expected_open else "❌"
                print(f"   {status} Open state: {is_open} (expected: {expected_open})")
            
            # Check contents
            contents = obj.get_contents()
            expected_contents = expectations.get("should_contain", [])
            for expected_item in expected_contents:
                if expected_item in contents:
                    print(f"   ✅ Contains: {expected_item}")
                else:
                    print(f"   ❌ Missing content: {expected_item}")
        
        # Check treasure status
        if expectations.get("treasure"):
            is_treasure = obj.get_attribute("treasure", False)
            value = obj.get_attribute("treasure_value", 0)
            status = "✅" if is_treasure else "❌"
            print(f"   {status} Treasure: {is_treasure}, Value: {value}")
        
        # Check light source
        if expectations.get("light_source"):
            is_light = obj.is_light_source()
            is_lit = obj.is_lit()
            print(f"   ✅ Light source: {is_light}, Currently lit: {is_lit}")

def main():
    """Run comprehensive canonical validation."""
    
    # Initialize game with MUD files
    game = GameEngine(use_mud_files=True)
    
    print("🎮 ZORK CANONICAL VALIDATION")
    print("Checking implementation against original 1978 specifications...")
    
    # Validate room objects
    missing_objects = validate_room_objects(game)
    
    # Validate object states  
    validate_object_states(game)
    
    # Summary report
    print(f"\n📊 VALIDATION SUMMARY")
    print("=" * 20)
    
    if missing_objects:
        print(f"❌ Found {len(missing_objects)} missing objects:")
        for room_id, obj_id in missing_objects:
            print(f"   • {obj_id} missing from {room_id}")
    else:
        print("✅ All expected objects found!")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("1. Add missing high-priority objects to rooms")
    print("2. Verify all container states match canonical expectations") 
    print("3. Test object interactions for authentic behavior")
    print("4. Cross-check treasure values and placement")

if __name__ == "__main__":
    main()