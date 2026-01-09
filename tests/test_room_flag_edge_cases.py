import unittest
from entities import Room

class TestRoomFlagEdgeCases(unittest.TestCase):
    def test_undefined_flag(self):
        room = Room(
            id="EDGE",
            desc_long="Edge case room.",
            desc_short="Edge Room",
            exits={},
            objects=[],
            flags=0,
        )
        UNDEFINED_FLAG = 0x1000
        room.set_flag(UNDEFINED_FLAG)
        self.assertTrue(room.has_flag(UNDEFINED_FLAG))
        room.clear_flag(UNDEFINED_FLAG)
        self.assertFalse(room.has_flag(UNDEFINED_FLAG))

    def test_multiple_flags(self):
        room = Room(
            id="MULTI",
            desc_long="Multiple flags room.",
            desc_short="Multi Room",
            exits={},
            objects=[],
            flags=0,
        )
        room.set_flag(Room.ROOM_DARK | Room.ROOM_DEADLY)
        self.assertTrue(room.has_flag(Room.ROOM_DARK))
        self.assertTrue(room.has_flag(Room.ROOM_DEADLY))
        room.clear_flag(Room.ROOM_DARK | Room.ROOM_DEADLY)
        self.assertFalse(room.has_flag(Room.ROOM_DARK))
        self.assertFalse(room.has_flag(Room.ROOM_DEADLY))

if __name__ == "__main__":
    unittest.main()
