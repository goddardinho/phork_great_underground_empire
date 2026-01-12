import io
import sys
import builtins
import pytest
from rooms import forest_room_action

class DummyGame:
    pass

def test_forest_room_action_go_in_prints_bird_sound(monkeypatch):
    output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", output)
    forest_room_action(DummyGame(), verb="GO-IN")
    sys.stdout = sys.__stdout__
    assert "chirping of a songbird" in output.getvalue()

def test_forest_room_action_c_int_prints_bird_sound(monkeypatch):
    output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", output)
    # Patch random.random to always return < 0.1
    monkeypatch.setattr("random.random", lambda: 0.05)
    forest_room_action(DummyGame(), verb="C-INT")
    sys.stdout = sys.__stdout__
    assert "chirping of a song bird" in output.getvalue()

def test_forest_room_action_c_int_no_sound(monkeypatch):
    output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", output)
    # Patch random.random to always return > 0.1
    monkeypatch.setattr("random.random", lambda: 0.5)
    forest_room_action(DummyGame(), verb="C-INT")
    sys.stdout = sys.__stdout__
    assert output.getvalue() == ""
