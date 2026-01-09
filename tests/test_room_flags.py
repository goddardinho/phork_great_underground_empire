import unittest
from entities import Room

class TestRoomFlags(unittest.TestCase):
    def setUp(self):
        self.room = Room(
            id="TEST",
            desc_long="Test room long description.",
            desc_short="Test room short description.",
            exits={},
            objects=[],
            flags=0,
        )

    def test_initial_flags(self):
        self.assertFalse(self.room.has_flag(Room.ROOM_DARK))
        self.assertFalse(self.room.has_flag(Room.ROOM_VISITED))
        self.assertFalse(self.room.has_flag(Room.ROOM_DEADLY))

    def test_set_flag(self):
        self.room.set_flag(Room.ROOM_DARK)
        self.assertTrue(self.room.has_flag(Room.ROOM_DARK))
        self.assertFalse(self.room.has_flag(Room.ROOM_VISITED))

    def test_clear_flag(self):
        self.room.set_flag(Room.ROOM_DARK)
        self.room.clear_flag(Room.ROOM_DARK)
        self.assertFalse(self.room.has_flag(Room.ROOM_DARK))

    def test_multiple_flags(self):
        self.room.set_flag(Room.ROOM_DARK)
        self.room.set_flag(Room.ROOM_DEADLY)
        self.assertTrue(self.room.has_flag(Room.ROOM_DARK))
        self.assertTrue(self.room.has_flag(Room.ROOM_DEADLY))
        self.room.clear_flag(Room.ROOM_DARK)
        self.assertFalse(self.room.has_flag(Room.ROOM_DARK))
        self.assertTrue(self.room.has_flag(Room.ROOM_DEADLY))

if __name__ == "__main__":
    unittest.main()
