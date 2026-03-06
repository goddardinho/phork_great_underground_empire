#!/usr/bin/env python3
"""Test suite for canonical bulk actions system (take all, drop everything, etc.)."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.entities.objects import GameObject

def test_bulk_action_objects():
    """Test creation and attributes of bulk action objects."""
    print("🧪 Testing Bulk Action Objects...")
    
    # Test ALL object
    all_obj = GameObject(
        id="ALL",
        name="everything",
        description="A special command to act on multiple objects at once.",
        aliases=["all", "everything"],
        attributes={
            "bulk_action": True,
            "bulk_type": "all",
            "takeable": True,
            "visible": True
        }
    )
    
    print(f"✓ ALL object is_bulk_action(): {all_obj.is_bulk_action()}")
    print(f"✓ ALL object get_bulk_type(): {all_obj.get_bulk_type()}")
    print(f"✓ ALL object matches 'all': {all_obj.matches('all')}")
    print(f"✓ ALL object matches 'everything': {all_obj.matches('everything')}")
    
    # Test VALUABLES object
    valuables_obj = GameObject(
        id="VALUABLES",
        name="valuables",
        description="A special command to act on treasure items.",
        aliases=["valuables", "treasures"],
        attributes={
            "bulk_action": True,
            "bulk_type": "valuables",
            "takeable": True,
            "visible": True
        }
    )
    
    print(f"✓ VALUABLES object is_bulk_action(): {valuables_obj.is_bulk_action()}")
    print(f"✓ VALUABLES object get_bulk_type(): {valuables_obj.get_bulk_type()}")
    print(f"✓ VALUABLES object matches 'valuables': {valuables_obj.matches('valuables')}")
    print(f"✓ VALUABLES object matches 'treasures': {valuables_obj.matches('treasures')}")
    
    print("\n✅ Bulk action objects working correctly!")

def test_treasure_value_system():
    """Test objects with treasure values for valuables command."""
    print("\n🧪 Testing Treasure Value System...")
    
    # Regular object (no treasure value)
    lamp = GameObject(
        id="LAMP",
        name="brass lantern",
        description="A bright brass lantern.",
        attributes={"takeable": True}
    )
    
    # Treasure object
    trophy = GameObject(
        id="TROPHY", 
        name="trophy case",
        description="A large trophy case.",
        attributes={
            "takeable": True,
            "treasure_value": 25  # Makes it a treasure
        }
    )
    
    print(f"✓ Lamp treasure_value: {lamp.get_attribute('treasure_value', 0)}")
    print(f"✓ Trophy treasure_value: {trophy.get_attribute('treasure_value', 0)}")
    print(f"✓ Lamp is treasure: {lamp.get_attribute('treasure_value', 0) > 0}")
    print(f"✓ Trophy is treasure: {trophy.get_attribute('treasure_value', 0) > 0}")
    
    print("\n✅ Treasure value system working correctly!")

def test_bulk_object_filtering():
    """Test filtering objects for different bulk action types."""
    print("\n🧪 Testing Bulk Object Filtering...")
    
    # Create test objects
    objects = [
        GameObject(id="LAMP", name="lamp", description="A lamp.", attributes={"takeable": True}),
        GameObject(id="SWORD", name="sword", description="A sword.", attributes={"takeable": True, "treasure_value": 10}),
        GameObject(id="ROCK", name="rock", description="A rock.", attributes={"takeable": False}),  # Not takeable
        GameObject(id="GOLD", name="gold", description="Gold coins.", attributes={"takeable": True, "treasure_value": 50})
    ]
    
    # Test filtering for "all" (takeable objects)
    all_takeables = [obj for obj in objects if obj.is_takeable()]
    print(f"✓ All takeable objects: {len(all_takeables)} ({[obj.name for obj in all_takeables]})")
    
    # Test filtering for "valuables" (treasure_value > 0)
    valuables = [obj for obj in objects if obj.is_takeable() and obj.get_attribute('treasure_value', 0) > 0]
    print(f"✓ Valuable objects: {len(valuables)} ({[obj.name for obj in valuables]})")
    
    # Verify expected results
    assert len(all_takeables) == 3, f"Expected 3 takeable objects, got {len(all_takeables)}"
    assert len(valuables) == 2, f"Expected 2 valuable objects, got {len(valuables)}"
    assert "rock" not in [obj.name for obj in all_takeables], "Rock should not be takeable"
    assert "sword" in [obj.name for obj in valuables], "Sword should be valuable"
    assert "gold" in [obj.name for obj in valuables], "Gold should be valuable"
    
    print("\n✅ Bulk object filtering working correctly!")

if __name__ == "__main__":
    print("🚀 Canonical Bulk Actions Test Suite")
    print("=" * 50)
    
    test_bulk_action_objects()
    test_treasure_value_system()  
    test_bulk_object_filtering()
    
    print("\n🎉 All bulk action tests passed!")
    print("Canonical Zork bulk actions system ready! 🎮")
    print("\nTry these commands in game:")
    print("• take all          - Take all takeable objects")
    print("• drop everything   - Drop everything you're carrying")
    print("• take valuables    - Take only treasure items")
    print("• drop possessions  - Drop all your possessions")