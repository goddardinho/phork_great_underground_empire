import unittest
from main import Game

class TestGameCommands(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.current_room = "WHOUS"
        self.game.rooms["WHOUS"].locked_exits = {"east": True}

    def test_quit_command(self):
        result = self.game.parse_command("quit")
        self.assertFalse(result)

    def test_look_command(self):
        result = self.game.parse_command("look")
        self.assertTrue(result)

    def test_locked_direction(self):
        result = self.game.parse_command("e")
        self.assertTrue(result)

    def test_unknown_command(self):
        result = self.game.parse_command("foobar")
        self.assertTrue(result)

    def test_inventory_command(self):
        result = self.game.parse_command("inventory")
        self.assertTrue(result)

class TestGameEdgeCases(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.current_room = "WHOUS"
        self.game.rooms["WHOUS"].locked_exits = {"east": True}

    def test_empty_command(self):
        result = self.game.parse_command("")
        self.assertTrue(result)

    def test_whitespace_command(self):
        result = self.game.parse_command("   ")
        self.assertTrue(result)

    def test_case_insensitivity(self):
        result = self.game.parse_command("LoOk")
        self.assertTrue(result)

    def test_partial_direction(self):
        result = self.game.parse_command("east")
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
