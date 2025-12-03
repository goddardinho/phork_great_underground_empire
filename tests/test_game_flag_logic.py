import unittest
from entities import Room
from main import Game
from io import StringIO
import sys

class TestGameFlagLogic(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.rooms["DARKROOM"] = Room(
            id="DARKROOM",
            desc_long="A pitch dark room.",
            desc_short="Dark Room",
            exits={},
            objects=[],
            flags=Room.ROOM_DARK,
        )
        self.game.current_room = "DARKROOM"

    def test_is_room_dark(self):
        self.assertTrue(self.game.is_room_dark("DARKROOM"))
        self.assertFalse(self.game.is_room_dark("WHOUS"))

    def test_check_room_flags_dark(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        self.game.check_room_flags()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("It is pitch dark. You are likely to be eaten by a grue.", output)

if __name__ == "__main__":
    unittest.main()
