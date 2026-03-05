"""Basic tests for the game foundation."""

# import pytest  # Optional for manual testing
from src.world.room import Room
from src.entities.player import Player
from src.entities.objects import GameObject
from src.parser.command_parser import CommandParser


def test_room_creation():
    """Test basic room functionality."""
    room = Room(id="TEST", name="Test Room", description="A test room")
    assert room.id == "TEST"
    assert room.name == "Test Room"
    assert not room.visited
    

def test_room_exits():
    """Test room exit functionality.""" 
    room = Room(id="ROOM1", name="Room 1", description="Test room", exits={"north": "ROOM2"})
    assert room.get_exit("north") == "ROOM2"
    assert room.get_exit("south") is None


def test_player_inventory():
    """Test player inventory management.""" 
    player = Player()
    assert player.get_inventory_count() == 0
    
    # Add item
    assert player.add_to_inventory("ITEM1") == True
    assert player.has_item("ITEM1") == True
    assert player.get_inventory_count() == 1
    
    # Remove item
    assert player.remove_from_inventory("ITEM1") == True
    assert player.has_item("ITEM1") == False
    assert player.get_inventory_count() == 0


def test_game_object():
    """Test game object functionality."""
    obj = GameObject(
        id="SWORD", 
        name="rusty sword", 
        description="An old, rusty sword.",
        attributes={"takeable": True, "weight": 3}
    )
    
    assert obj.is_takeable() == True
    assert obj.get_weight() == 3
    assert obj.is_container() == False  # Default


def test_command_parsing():
    """Test command parser functionality."""
    parser = CommandParser()
    
    # Simple verb
    cmd = parser.parse("look")
    assert cmd.verb == "look"
    assert cmd.noun is None
    
    # Verb with object
    cmd = parser.parse("take sword")
    assert cmd.verb == "take"
    assert cmd.noun == "sword"
    
    # Direction synonyms
    cmd = parser.parse("n")
    assert cmd.verb == "north"
    
    # Complex command
    cmd = parser.parse("put sword in chest")
    assert cmd.verb == "put"
    assert cmd.noun == "sword" 
    assert cmd.preposition == "in"
    assert cmd.noun2 == "chest"


if __name__ == "__main__":
    # Run tests manually if pytest not available
    test_room_creation()
    test_room_exits()
    test_player_inventory()
    test_game_object()
    test_command_parsing()
    print("All tests passed!")