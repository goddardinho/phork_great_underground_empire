import unittest
from entities import Room
from main import load_rooms
import pickle

class TestRoomFlagsExtended(unittest.TestCase):
    def test_room_creation_flags(self):
        rooms = load_rooms()
        troll_room = rooms.get("TROLL")
        self.assertIsNotNone(troll_room)
        self.assertTrue(troll_room.has_flag(Room.ROOM_DEADLY))
        house_room = rooms.get("HOUSE")
        self.assertIsNotNone(house_room)
        self.assertFalse(house_room.has_flag(Room.ROOM_DARK))
        self.assertFalse(house_room.has_flag(Room.ROOM_DEADLY))

    def test_game_logic_is_room_dark(self):
        room = Room(
            id="DARKROOM",
            desc_long="A pitch dark room.",
            desc_short="Dark Room",
            exits={},
            objects=[],
            flags=Room.ROOM_DARK,
        )
        self.assertTrue(room.has_flag(Room.ROOM_DARK))

    def test_edge_cases_flags(self):
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
        room.set_flag(Room.ROOM_DARK | Room.ROOM_DEADLY)
        self.assertTrue(room.has_flag(Room.ROOM_DARK))
        self.assertTrue(room.has_flag(Room.ROOM_DEADLY))
        room.clear_flag(Room.ROOM_DARK | Room.ROOM_DEADLY)
        self.assertFalse(room.has_flag(Room.ROOM_DARK))
        self.assertFalse(room.has_flag(Room.ROOM_DEADLY))

    def test_serialization_flags(self):
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

if __name__ == "__main__":
    unittest.main()
