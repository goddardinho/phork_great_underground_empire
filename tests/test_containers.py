import unittest
from objects import GameObject
from containers import Container

class TestContainerMechanics(unittest.TestCase):
    def test_basic_container(self):
        box = Container('Box', 'A simple box.', max_items=2)
        item1 = GameObject('Apple', 'A red apple.')
        item2 = GameObject('Banana', 'A yellow banana.')
        self.assertEqual(box.open(), 'You open the Box.')
        self.assertEqual(box.look_inside(), 'The Box is empty.')
        self.assertEqual(box.add_object(item1), 'You put the Apple in the Box.')
        self.assertEqual(box.add_object(item2), 'You put the Banana in the Box.')
        self.assertIn(item1, box.attributes['contents'])
        self.assertIn(item2, box.attributes['contents'])
        # Test max_items limit
        item3 = GameObject('Orange', 'A juicy orange.')
        msg = box.add_object(item3)
        self.assertIn("can't hold any more items", msg)
        # Remove item
        self.assertEqual(box.remove_object(item1), 'You take the Apple from the Box.')
        self.assertNotIn(item1, box.attributes['contents'])

    def test_nested_containers(self):
        chest = Container('Chest', 'A large chest.', max_items=3)
        box = Container('Box', 'A small box.', max_items=1)
        gem = GameObject('Gem', 'A sparkling gem.')
        chest.open()
        box.open()
        self.assertEqual(chest.add_object(box), 'You put the Box in the Chest.')
        self.assertEqual(box.add_object(gem), 'You put the Gem in the Box.')
        self.assertIn(box, chest.attributes['contents'])
        self.assertIn(gem, box.attributes['contents'])
        # Recursive look inside
        desc = chest.look_inside(recursive=True, depth=2)
        self.assertIn('Gem', desc)

    def test_lock_unlock(self):
        safe = Container('Safe', 'A locked safe.')
        self.assertEqual(safe.lock(), 'You lock the Safe.')
        self.assertEqual(safe.open(), 'The Safe is locked.')
        self.assertEqual(safe.unlock(), 'You unlock the Safe.')
        self.assertEqual(safe.open(), 'You open the Safe.')

if __name__ == '__main__':
    unittest.main()
