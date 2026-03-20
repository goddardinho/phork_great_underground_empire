import unittest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.world.room import Room

class TestRoomFlagEdgeCases(unittest.TestCase):
    def test_undefined_flag(self):
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

    def test_multiple_flags(self):
        room = Room(
            id="MULTI",
            description="Multiple flags room.",
            name="Multi Room",
            exits={},
            items=[],
            flags=set(),
        )
        # Set multiple flags using individual calls
        room.set_flag(Room.ROOM_DARK)
        room.set_flag(Room.ROOM_DEADLY)
        self.assertTrue(room.has_flag(Room.ROOM_DARK))
        self.assertTrue(room.has_flag(Room.ROOM_DEADLY))
        
        # Clear multiple flags
        room.clear_flag(Room.ROOM_DARK)
        room.clear_flag(Room.ROOM_DEADLY)
        self.assertFalse(room.has_flag(Room.ROOM_DARK))
        self.assertFalse(room.has_flag(Room.ROOM_DEADLY))

if __name__ == "__main__":
    unittest.main()
