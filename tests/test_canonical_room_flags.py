import io
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    
import unittest
from src.world.room import Room
from src.entities.player import Player
from src.game import GameEngine as Game

class DummyPlayer(Player):
    def __init__(self):
        super().__init__("Tester", "SAFE")
        self.health = 10
        self.max_health = 10
        self.staggered = False
    def is_dead(self):
        return self.health <= 0

def test_safe_room_prevents_death():
    game = Game()
    safe_room = Room("SAFE", "A safe room.", "Safe Room", {}, [], flags=Room.ROOM_SAFE)
    game.rooms = {"SAFE": safe_room}
    game.current_room = "SAFE"
    game.player = DummyPlayer()
    output = io.StringIO()
    sys.stdout = output
    game.game_over("You have died.")
    sys.stdout = sys.__stdout__
    assert "safe" in output.getvalue().lower()
    assert "harm" in output.getvalue().lower()

def test_no_save_room_blocks_save():
    game = Game()
    no_save_room = Room("NOSAVE", "No save here.", "NoSave Room", {}, [], flags=Room.ROOM_NO_SAVE)
    game.rooms = {"NOSAVE": no_save_room}
    game.current_room = "NOSAVE"
    output = io.StringIO()
    sys.stdout = output
    game.save_game("dummy_save.pkl")
    sys.stdout = sys.__stdout__
    assert "cannot save" in output.getvalue().lower()

def test_no_restore_room_blocks_restore():
    game = Game()
    no_restore_room = Room("NORESTORE", "No restore here.", "NoRestore Room", {}, [], flags=Room.ROOM_NO_RESTORE)
    game.rooms = {"NORESTORE": no_restore_room}
    game.current_room = "NORESTORE"
    output = io.StringIO()
    sys.stdout = output
    game.load_game("dummy_save.pkl")
    sys.stdout = sys.__stdout__
    assert "cannot restore" in output.getvalue().lower()

def test_water_room_requires_boat():
    game = Game()
    water_room = Room("WATER", "A watery room.", "Water Room", {"north": "SAFE"}, [], flags=Room.ROOM_WATER)
    safe_room = Room("SAFE", "A safe room.", "Safe Room", {}, [], flags=Room.ROOM_SAFE)
    game.rooms = {"WATER": water_room, "SAFE": safe_room}
    game.current_room = "WATER"
    output = io.StringIO()
    sys.stdout = output
    game.move("north")
    sys.stdout = sys.__stdout__
    assert "drown" in output.getvalue().lower()
    # Now test with boat
    game.inventory.append(type("Obj", (), {"name": "Boat"})())
    output = io.StringIO()
    sys.stdout = output
    game.move("north")
    sys.stdout = sys.__stdout__
    assert "safe room" in output.getvalue().lower()

def test_air_room_requires_mask():
    game = Game()
    air_room = Room("AIR", "An airy room.", "Air Room", {"north": "SAFE"}, [], flags=Room.ROOM_AIR)
    safe_room = Room("SAFE", "A safe room.", "Safe Room", {}, [], flags=Room.ROOM_SAFE)
    game.rooms = {"AIR": air_room, "SAFE": safe_room}
    game.current_room = "AIR"
    output = io.StringIO()
    sys.stdout = output
    game.move("north")
    sys.stdout = sys.__stdout__
    assert "suffocat" in output.getvalue().lower()
    # Now test with mask
    game.inventory.append(type("Obj", (), {"name": "Mask"})())
    output = io.StringIO()
    sys.stdout = output
    game.move("north")
    sys.stdout = sys.__stdout__
    assert "safe room" in output.getvalue().lower()

def test_visited_flag_set_on_entry():
    game = Game()
    room = Room("VISIT", "A room to visit.", "Visit Room", {}, [], flags=0)
    game.rooms = {"VISIT": room}
    game.current_room = "VISIT"
    assert not getattr(room, "visited", False)
    game.describe_current_room()
    assert getattr(room, "visited", False)
