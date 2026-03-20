import unittest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.world.room import Room
from src.game import GameEngine
import pickle

class TestRoomFlagsExtended(unittest.TestCase):
    def test_room_creation_flags(self):
        # Create a simple game to test room flags
        game = GameEngine(use_mud_files=False)  # Use test world
        
        # Test basic room flag functionality
        test_room = Room(
            id="TEST_DEADLY",
            name="Deadly Room",
            description="A dangerous room.",
            flags={Room.ROOM_DEADLY, Room.ROOM_DARK}
        )
        
        self.assertTrue(test_room.has_flag(Room.ROOM_DEADLY))
        self.assertTrue(test_room.has_flag(Room.ROOM_DARK))
        self.assertFalse(test_room.has_flag(Room.ROOM_SACRED))

    def test_game_logic_is_room_dark(self):
        room = Room(
            id="DARKROOM",
            description="A pitch dark room.",
            name="Dark Room",
            exits={},
            items=[],
            flags={Room.ROOM_DARK},
        )
        self.assertTrue(room.has_flag(Room.ROOM_DARK))

    def test_edge_cases_flags(self):
        room = Room(
            id="EDGE",
            description="Edge case room.",
            name="Edge Room",
            exits={},
            items=[],
            flags=set(),
        )
        UNDEFINED_FLAG = "undefined_flag"
        room.set_flag(UNDEFINED_FLAG)
        self.assertTrue(room.has_flag(UNDEFINED_FLAG))
        room.clear_flag(UNDEFINED_FLAG)
        self.assertFalse(room.has_flag(UNDEFINED_FLAG))
        
        # Set multiple flags using individual calls (no bitwise operations on strings)
        room.set_flag(Room.ROOM_DARK)
        room.set_flag(Room.ROOM_DEADLY)
        self.assertTrue(room.has_flag(Room.ROOM_DARK))
        self.assertTrue(room.has_flag(Room.ROOM_DEADLY))
        
        # Clear multiple flags
        room.clear_flag(Room.ROOM_DARK)
        room.clear_flag(Room.ROOM_DEADLY)
        self.assertFalse(room.has_flag(Room.ROOM_DARK))
        self.assertFalse(room.has_flag(Room.ROOM_DEADLY))

    def test_serialization_flags(self):
        room = Room(
            id="SERIAL",
            description="Serialization test room.",
            name="Serial Room",
            exits={},
            items=[],
            flags={Room.ROOM_DARK, Room.ROOM_DEADLY},
        )
        data = pickle.dumps(room)
        loaded_room = pickle.loads(data)
        self.assertTrue(loaded_room.has_flag(Room.ROOM_DARK))
        self.assertTrue(loaded_room.has_flag(Room.ROOM_DEADLY))

if __name__ == "__main__":
    unittest.main()
