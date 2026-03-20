#!/usr/bin/env python3
"""
Comprehensive validation of canonical Zork objects and locations.
Checks against original 1978 MIT Zork specifications.
"""

from src.game import GameEngine

def validate_canonical_objects():
    """Validate all canonical objects are present with correct properties."""
    print("🧪 COMPREHENSIVE CANONICAL OBJECT VALIDATION")
    print("=" * 60)
    
    # Initialize game
    game = GameEngine(use_mud_files=True)
    
    # Expected canonical objects with their specifications
    expected_objects = {
        # Starting area objects
        "MAILBOX": {
            "location": "SHOUS",  # South of House - canonical location
            "takeable": False,
            "container": True,
            "open": False,  # Starts closed
            "contents": ["LEAFLET"],
            "description_contains": ["mailbox", "small"]
        },
        "LEAFLET": {
            "location": "MAILBOX",  # Inside mailbox initially
            "takeable": True,
            "readable": True,
            "description_contains": ["leaflet", "promotional"]
        },
        
        # Living Room objects (LROOM)
        "TCASE": {
            "location": "LROOM",
            "takeable": False,
            "container": True,
            "open": False,  # Trophy case starts closed
            "description_contains": ["trophy", "case"]
        },
        "RUG": {
            "location": "LROOM", 
            "takeable": False,
            "moveable": True,  # Can be moved to reveal trap door
            "description_contains": ["rug", "oriental"]
        },
        "SWORD": {
            "location": "LROOM",
            "takeable": True,
            "weapon": True,
            "treasure": True,
            "treasure_value": 10,
            "description_contains": ["sword", "elvish"]
        },
        "LAMP": {
            "location": "LROOM",
            "takeable": True,
            "light_source": True,
            "treasure": True,
            "treasure_value": 10,
            "lit": False,  # Starts unlit
            "description_contains": ["lamp", "brass"]
        },
        
        # Kitchen objects (KITCH)
        "BOTTL": {
            "location": "KITCH",
            "takeable": True,
            "container": True,
            "open": True,  # Bottle has open top
            "description_contains": ["bottle", "glass"]
        },
        "SBAG": {
            "location": "KITCH",
            "takeable": True,
            "container": True,
            "open": False,  # Sack starts closed
            "contents": ["GARLIC"],  # Often contains garlic
            "description_contains": ["sack", "bag", "brown"]
        },
        "GARLIC": {
            "location": "SBAG",  # Inside sack initially
            "takeable": True,
            "description_contains": ["garlic", "clove"]
        },
        
        # Tree room objects (TREE)
        "NEST": {
            "location": "TREE",
            "takeable": True,
            "container": True,
            "open": True,  # Nest starts open so egg is visible
            "contents": ["EGG"],
            "description_contains": ["nest", "bird"]
        },
        "EGG": {
            "location": "NEST",  # Inside nest initially
            "takeable": True,
            "treasure": True,
            "treasure_value": 5,
            "container": True,  # Egg can be opened
            "open": False,  # Starts closed
            "description_contains": ["egg", "jewel"]
        },
        "TTREE": {
            "location": "TREE",
            "takeable": False,
            "weight": 1000,  # Very heavy
            "description_contains": ["tree", "large"]
        },
        
        # Other key canonical objects
        "WINDO": {
            "location": "EHOUS",  # Behind House (EHOUS)
            "takeable": False,
            "openable": True,
            "open": True,  # Window starts slightly ajar
            "door": True,  # Acts as passage
            "description_contains": ["window", "small"]
        },
        "GRATE": {
            "location": "MGRAT",  # Grating Room
            "takeable": False,
            "openable": True,
            "open": False,  # Starts closed
            "locked": True,  # Starts locked
            "door": True,  # Acts as passage when open
            "description_contains": ["grate", "metal"]
        },
        "TORCH": {
            "location": "ATTIC",  # Often in attic or other rooms
            "takeable": True,
            "light_source": True,
            "lit": False,  # Starts unlit
            "description_contains": ["torch", "wooden"]
        }
    }
    
    print(f"Checking {len(expected_objects)} canonical objects...")
    print()
    
    success_count = 0
    total_checks = 0
    
    for obj_id, expected in expected_objects.items():
        print(f"🔍 Validating {obj_id}...")
        total_checks += 1
        
        # Check if object exists
        obj = game.object_manager.get_object(obj_id)
        if not obj:
            print(f"❌ {obj_id}: Object not found!")
            continue
            
        # Check location (improved method)
        expected_location = expected.get("location")
        actual_location = None
        location_type = "unknown"
        
        if expected_location:
            # Check if it's supposed to be in a room
            target_room = game.world.get_room(expected_location)
            if target_room and obj_id in target_room.items:
                location_type = "room"
                actual_location = expected_location
            else:
                # Check if it's supposed to be in a container
                target_container = game.object_manager.get_object(expected_location)
                if target_container and target_container.is_container() and obj_id in target_container.get_contents():
                    location_type = "container"
                    actual_location = expected_location
                else:
                    # Search all rooms for this object
                    for room_id, room in game.world.rooms.items():
                        if obj_id in room.items:
                            location_type = "room"
                            actual_location = room_id
                            break
                    
                    # If not found in rooms, search containers
                    if location_type == "unknown":
                        for container_id, container_obj in game.object_manager.objects.items():
                            if container_obj.is_container() and obj_id in container_obj.get_contents():
                                location_type = "container"
                                actual_location = container_id
                                break
        
        if expected_location:
            if actual_location == expected_location:
                print(f"   ✓ Location: {expected_location}")
            else:
                print(f"   ❌ Location: Expected {expected_location}, found {location_type}:{actual_location}")
                continue
        
        # Check properties
        property_errors = []
        
        for prop, expected_value in expected.items():
            if prop in ["location", "description_contains", "contents"]:
                continue  # Handle separately
                
            actual_value = obj.get_attribute(prop)
            if actual_value != expected_value:
                property_errors.append(f"{prop}: expected {expected_value}, got {actual_value}")
        
        # Check description content
        if "description_contains" in expected:
            desc_lower = obj.description.lower()
            missing_words = []
            for word in expected["description_contains"]:
                if word.lower() not in desc_lower:
                    missing_words.append(word)
            if missing_words:
                property_errors.append(f"description missing: {missing_words}")
        
        # Check container contents
        if "contents" in expected and obj.is_container():
            actual_contents = obj.get_contents()
            expected_contents = expected["contents"]
            if set(actual_contents) != set(expected_contents):
                property_errors.append(f"contents: expected {expected_contents}, got {actual_contents}")
        
        if property_errors:
            print(f"   ❌ Property errors:")
            for error in property_errors:
                print(f"      - {error}")
        else:
            print(f"   ✓ All properties correct")
            success_count += 1
            
        print()
    
    # Check room connectivity for key locations
    print("🗺️  VALIDATING KEY ROOM CONNECTIONS")
    print("=" * 40)
    
    key_rooms = ["WHOUS", "LROOM", "KITCH", "TREE", "EHOUS", "MGRAT"]
    for room_id in key_rooms:
        room = game.world.get_room(room_id)
        if room:
            print(f"✓ {room_id}: {room.name}")
            # Count objects in room
            if room.items:
                print(f"   Objects: {room.items}")
        else:
            print(f"❌ {room_id}: Room not found!")
    
    print()
    print("📊 VALIDATION SUMMARY")
    print("=" * 30)
    print(f"Objects validated: {success_count}/{total_checks}")
    print(f"Success rate: {(success_count/total_checks)*100:.1f}%")
    
    if success_count == total_checks:
        print("🎉 ALL CANONICAL OBJECTS VALIDATED SUCCESSFULLY!")
    else:
        print(f"⚠️  {total_checks - success_count} objects need attention")
    
    return success_count == total_checks

if __name__ == "__main__":
    validate_canonical_objects()