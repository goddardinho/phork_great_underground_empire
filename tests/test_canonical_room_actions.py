import io
import sys
import pytest
from rooms import (
    kitchen_action, living_room_action, echo_room_action, mirror_room_action,
    maint_room_action, cyclops_room_action, treasure_room_action,
    grue_function_action, tomb_function_action
)

class DummyGame:
    pass

def capture_action_output(action_func, *args, **kwargs):
    output = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = output
    try:
        action_func(DummyGame(), *args, **kwargs)
    finally:
        sys.stdout = sys_stdout
    return output.getvalue()

def test_kitchen_action_look():
    out = capture_action_output(kitchen_action, verb="LOOK")
    assert "kitchen" in out

def test_living_room_action_look():
    out = capture_action_output(living_room_action, verb="LOOK")
    assert "living room" in out

def test_echo_room_action_look():
    out = capture_action_output(echo_room_action, verb="LOOK")
    assert "echo room" in out

def test_mirror_room_action_look():
    out = capture_action_output(mirror_room_action, verb="LOOK")
    assert "mirror room" in out

def test_maint_room_action_cint():
    out = capture_action_output(maint_room_action, verb="C-INT")
    assert "water level" in out.lower() or "flood" in out.lower()

def test_cyclops_room_action_look():
    out = capture_action_output(cyclops_room_action, verb="LOOK")
    assert "cyclops" in out

def test_treasure_room_action_goin():
    out = capture_action_output(treasure_room_action, verb="GO-IN")
    assert "thief" in out.lower() or "defend" in out.lower()

def test_grue_function_action_exami():
    out = capture_action_output(grue_function_action, verb="EXAMI")
    assert "grue" in out.lower()

def test_tomb_function_action_look():
    out = capture_action_output(tomb_function_action, verb="LOOK")
    assert "tomb" in out.lower()
