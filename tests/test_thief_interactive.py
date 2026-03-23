#!/usr/bin/env python3
"""Quick interactive test for Thief NPC functionality."""

import sys
from pathlib import Path

# Add src to Python path (from tests directory, go up one level to find src)
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Alternative: add root directory to path for src module access
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from src.game import GameEngine


def test_thief_interaction():
    """Test Thief NPC interactions in live gameplay."""
    print("🎮 Starting Thief Interactive Test...")
    game = GameEngine(debug_mode=True)
    
    # Check if Thief exists  
    thief = game.npc_manager.get_npc("THIEF")
    if thief:
        print(f"✅ Thief found at location: {thief.location}")
        
        # Test look command to see Thief
        print("\n🔍 Testing 'look' command:")
        game._process_command("look")
        
        # Test taking an item and then letting Thief steal it
        # First add a test treasure to room
        from src.entities.objects import GameObject
        treasure = GameObject(
            id="TEMP_TREASURE",
            name="silver coin",
            description="A shiny silver coin.",
            attributes={"treasure_value": 5, "takeable": True}
        )
        game.object_manager.add_object(treasure)
        
        # Add to current room
        current_room = game.world.get_room(game.player.current_room)
        if current_room:
            current_room.add_item("TEMP_TREASURE")
        
            print("\n📚 Testing item pickup and theft:")
            print("Taking the silver coin...")
            game._process_command("take silver coin")
            
            print("\\nWaiting for Thief to attempt theft...")
            
            # Force theft attempt by processing a dummy command
            if hasattr(thief, 'thief_behavior'):
                thief.thief_behavior.last_theft_time = 0  # Enable theft
                
            game._process_command("look")  # This will trigger theft check
        
        # Test dialogue
        print("\\n💬 Testing dialogue with Thief:")
        print("  Testing NPC search...")
        found_npc = game.npc_manager.find_npc_by_name("thief", game.player.current_room)
        if found_npc:
            print(f"  ✅ Found NPC: {found_npc.name}")
            print("  Starting conversation...")
            dialogue = game.npc_manager.start_conversation(found_npc.id)
            if dialogue:
                print(f"  Dialogue: {dialogue}")
            else:
                print("  ❌ No dialogue returned")
        else:
            print("  ❌ NPC not found")
        game._process_command("talk thief")
        
        # Test combat  
        print("\\n⚔️  Testing combat with Thief:")
        print("Attacking the Thief...")
        game._process_command("attack thief")
        
    else:
        print("❌ Thief NPC not found!")
    
    print("\\n✨ Interactive test complete!")
    print("\\n💡 Usage note:")
    print("   Run from project root: cd ../; python tests/test_thief_interactive.py")
    print("   Or run comprehensive debug: python tests/debug_thief_npc.py")


if __name__ == "__main__":
    test_thief_interaction()