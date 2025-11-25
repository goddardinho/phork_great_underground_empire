import unittest
from objects import GameObject
from containers import Container

class TestNesting(unittest.TestCase):
    def test_nested_location(self):
        chest = Container('Chest', 'A large chest.', max_items=3)
        box = Container('Box', 'A small box.', max_items=1)
        gem = GameObject('Gem', 'A sparkling gem.')
        chest.open()
        box.open()
        chest.add_object(box)
        box.add_object(gem)
        self.assertEqual(box.location, chest)
        self.assertEqual(gem.location, box)
        # Remove gem from box
        box.remove_object(gem)
        self.assertIsNone(gem.location)
        # Remove box from chest
        chest.remove_object(box)
        self.assertIsNone(box.location)

if __name__ == '__main__':
    unittest.main()
