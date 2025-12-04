import unittest
import pickle
from entities import Room

class TestRoomSerialization(unittest.TestCase):
    def test_flags_serialization(self):
        room = Room(
            id="SERIAL",
            desc_long="Serialization test room.",
            desc_short="Serial Room",
            exits={},
            objects=[],
            flags=Room.ROOM_DARK | Room.ROOM_DEADLY,
        )
        data = pickle.dumps(room)
        loaded_room = pickle.loads(data)
        self.assertTrue(loaded_room.has_flag(Room.ROOM_DARK))
        self.assertTrue(loaded_room.has_flag(Room.ROOM_DEADLY))
        self.assertFalse(loaded_room.has_flag(Room.ROOM_VISITED))

if __name__ == "__main__":
    unittest.main()
