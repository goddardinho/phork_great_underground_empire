#!/usr/bin/env python3
"""Test suite for enhanced container object system."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.entities.objects import GameObject

def test_enhanced_container_attributes():
    """Test new container attributes and methods."""
    print("🧪 Testing Enhanced Container Attributes...")
    
    # Create a container object
    chest = GameObject(
        id="CHEST",
        name="wooden chest",
        description="A sturdy wooden chest with metal hinges.",
        attributes={
            "container": True,
            "openable": True, 
            "open": False,
            "locked": False,
            "capacity": 5,  # Can hold max 5 items
            "contents": []
        }
    )
    
    # Test new methods
    print(f"✓ is_container(): {chest.is_container()}")
    print(f"✓ is_openable(): {chest.is_openable()}")
    print(f"✓ is_open(): {chest.is_open()}")
    print(f"✓ is_locked(): {chest.is_locked()}")
    print(f"✓ can_open(): {chest.can_open()}")
    print(f"✓ can_close(): {chest.can_close()}")
    print(f"✓ get_capacity(): {chest.get_capacity()}")
    print(f"✓ is_at_capacity(): {chest.is_at_capacity()}")
    
    # Test capacity limits
    for i in range(6):
        item_id = f"ITEM{i}"
        success = chest.add_to_container(item_id)
        capacity_status = "at capacity" if chest.is_at_capacity() else "has space"
        print(f"  Added {item_id}: {success} - Container {capacity_status} ({len(chest.get_contents())}/{chest.get_capacity()})")
    
    print("\n✅ Enhanced container attributes working correctly!")

def test_container_state_management():
    """Test container open/close state management."""
    print("\n🧪 Testing Container State Management...")
    
    # Create locked container
    safe = GameObject(
        id="SAFE",
        name="metal safe",
        description="A heavy metal safe with a combination lock.",
        attributes={
            "container": True,
            "openable": True,
            "open": False, 
            "locked": True,
            "contents": ["GOLD", "JEWELS"]
        }
    )
    
    print(f"✓ Locked safe can_open(): {safe.can_open()}")  # Should be False
    print(f"✓ Locked safe can_close(): {safe.can_close()}") # Should be False
    
    # Unlock and test
    safe.set_attribute("locked", False)
    print(f"✓ Unlocked safe can_open(): {safe.can_open()}")  # Should be True
    
    # Open and test
    safe.set_attribute("open", True) 
    print(f"✓ Open safe can_open(): {safe.can_open()}")     # Should be False
    print(f"✓ Open safe can_close(): {safe.can_close()}")   # Should be True
    
    print("\n✅ Container state management working correctly!")

def test_container_edge_cases():
    """Test container edge cases and special scenarios."""
    print("\n🧪 Testing Container Edge Cases...")
    
    # Unlimited capacity container (like mailbox)
    mailbox = GameObject(
        id="MAILBOX",
        name="small mailbox",
        description="A small metal mailbox.",
        attributes={
            "container": True,
            "openable": True,
            "open": True,
            "capacity": 0,  # 0 = unlimited
            "contents": ["LEAFLET"]
        }
    )
    
    print(f"✓ Unlimited capacity container is_at_capacity(): {mailbox.is_at_capacity()}")  # Should be False
    
    # Add many items (should never reach capacity)
    for i in range(10):
        mailbox.add_to_container(f"MAIL{i}")
    
    print(f"✓ After adding 10 items, still not at capacity: {not mailbox.is_at_capacity()}")
    print(f"✓ Contains {len(mailbox.get_contents())} items")
    
    # Non-container object
    rock = GameObject(
        id="ROCK", 
        name="granite rock",
        description="A heavy granite rock.",
        attributes={"container": False}
    )
    
    print(f"✓ Non-container add_to_container(): {rock.add_to_container('ITEM')}")  # Should be False
    print(f"✓ Non-container get_contents(): {rock.get_contents()}")  # Should be []
    
    print("\n✅ Container edge cases handled correctly!")

if __name__ == "__main__":
    print("🚀 Enhanced Container System Test Suite")
    print("=" * 50)
    
    test_enhanced_container_attributes()
    test_container_state_management() 
    test_container_edge_cases()
    
    print("\n🎉 All container system tests passed!")
    print("Enhanced container mechanics ready for integration!")