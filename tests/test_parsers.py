import unittest
from parsers import parse_exits, parse_objects, parse_flags, parse_action
from entities import Room, Player, Action
from objects import GameObject

class TestParsers(unittest.TestCase):
    def test_parse_exits(self):
        exits_str = '<EXIT "north" "ROOM1"><EXIT "south" "ROOM2"><EXIT "east" "ROOM3">'
        exits = parse_exits(exits_str)
        self.assertEqual(exits, {'north': 'ROOM1', 'south': 'ROOM2', 'east': 'ROOM3'})

    def test_parse_objects(self):
        objects_str = '<OBJ "Lantern" "An old lantern"><OBJ "Key" "A rusty key">'
        objects = parse_objects(objects_str)
        self.assertEqual(objects[0].name, 'Lantern')
        self.assertEqual(objects[0].description, 'An old lantern')
        self.assertEqual(objects[1].name, 'Key')
        self.assertEqual(objects[1].description, 'A rusty key')

    def test_parse_flags(self):
        flags_str = '<FLAGWORD dark visited locked>'
        flags = parse_flags(flags_str)
        self.assertIn('dark', flags)
        self.assertIn('visited', flags)
        self.assertIn('locked', flags)

    def test_parse_action(self):
        line = '<RACTION "test_action">'
        action_name = parse_action(line)
        self.assertEqual(action_name, 'test_action')

class TestRoomAndPlayer(unittest.TestCase):
    def test_room_creation(self):
        room = Room('ROOM1', 'A test room.', 'Test', {'north': 'ROOM2'}, [], ['dark'])
        self.assertEqual(room.id, 'ROOM1')
        self.assertIn('north', room.exits)
        self.assertIn('dark', room.flags)

    def test_player_inventory(self):
        player = Player('Hero', 'ROOM1')
        obj = GameObject('Lantern', 'A lantern.')
        player.inventory.append(obj)
        self.assertIn(obj, player.inventory)
        self.assertEqual(player.current_room, 'ROOM1')

if __name__ == '__main__':
    unittest.main()
