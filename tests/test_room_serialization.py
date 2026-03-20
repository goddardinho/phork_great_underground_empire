import unittest
import pickle
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.world.room import Room

class TestRoomSerialization(unittest.TestCase):
    def test_flags_serialization(self):
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
        self.assertFalse(loaded_room.has_flag(Room.ROOM_VISITED))

if __name__ == "__main__":
    unittest.main()
