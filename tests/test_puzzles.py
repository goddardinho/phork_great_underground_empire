import unittest
from puzzles import trigger_puzzle, PUZZLE_REGISTRY

class DummyGame:
    def __init__(self):
        self.puzzles = {}
        self.score = 0

class TestPuzzles(unittest.TestCase):
    def test_button_puzzle(self):
        game = DummyGame()
        result = trigger_puzzle(game, "push button")
        self.assertTrue(result)
        self.assertEqual(game.score, 7)
        self.assertTrue(game.puzzles["button_puzzle"])
        # Repeat should fail and not change score
        result2 = trigger_puzzle(game, "push button")
        self.assertFalse(result2)
        self.assertEqual(game.score, 7)

    def test_mailbox_puzzle(self):
        game = DummyGame()
        result = trigger_puzzle(game, "open mailbox")
        self.assertTrue(result)
        self.assertEqual(game.score, 1)
        self.assertTrue(game.puzzles["mailbox_puzzle"])
        result2 = trigger_puzzle(game, "open mailbox")
        self.assertFalse(result2)
        self.assertEqual(game.score, 1)

    def test_unlock_door_puzzle(self):
        game = DummyGame()
        result = trigger_puzzle(game, ("unlock", "north"))
        self.assertTrue(result)
        self.assertEqual(game.score, 2)
        self.assertTrue(game.puzzles["unlock_door_north"])
        result2 = trigger_puzzle(game, ("unlock", "north"))
        self.assertFalse(result2)
        self.assertEqual(game.score, 2)

    def test_grue_puzzle(self):
        game = DummyGame()
        result = trigger_puzzle(game, "enter dark room")
        self.assertTrue(result)
        self.assertEqual(game.score, -5)
        self.assertTrue(game.puzzles["grue_puzzle"])
        result2 = trigger_puzzle(game, "enter dark room")
        self.assertFalse(result2)
        self.assertEqual(game.score, -5)

    def test_victory_puzzle(self):
        game = DummyGame()
        result = trigger_puzzle(game, "win game")
        self.assertTrue(result)
        self.assertEqual(game.score, 35)
        self.assertTrue(game.puzzles["victory_puzzle"])
        result2 = trigger_puzzle(game, "win game")
        self.assertFalse(result2)
        self.assertEqual(game.score, 35)

if __name__ == "__main__":
    unittest.main()
