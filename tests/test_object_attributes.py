import pytest
from objects import GameObject
from containers import Container
from main import Game

@pytest.fixture
def game():
    g = Game(demo_mode=False)
    g.rooms = {}
    g.current_room = "TEST"
    g.rooms["TEST"] = type(
        "Room",
        (),
        {
            "objects": [],
            "npcs": [],
            "exits": {},
            "id": "TEST",
            "has_flag": lambda self, x: True,
        },
    )()
    return g

def make_obj(name, **attrs):
    return GameObject(name, f"A {name} for testing.", attributes=attrs)

def test_touched_on_take(game):
    obj = make_obj("foo", takeable=True, portable=True)
    game.rooms["TEST"].objects.append(obj)
    game.parse_command("take foo")
    assert obj.attributes["touched"] is True

def test_recursive_searchable(game, capsys):
    inner = make_obj("inner", takeable=True, portable=True)
    outer = Container("outer", "Outer container", attributes={"searchable": True, "open": True, "container": True, "contents": [inner]})
    game.rooms["TEST"].objects.append(outer)
    game.parse_command("search outer")
    out = capsys.readouterr().out
    assert "inner" in out

def test_light_on_logic(game):
    lamp = make_obj("lamp", light=True, lit=True)
    game.inventory.append(lamp)
    assert not game.is_room_dark()

def test_actor_inventory_search(game, capsys):
    actor = make_obj("npc", actor=True)
    item = make_obj("coin", takeable=True)
    actor.inventory = [item]
    game.rooms["TEST"].objects.append(actor)
    game.parse_command("examine npc")
    out = capsys.readouterr().out
    assert "coin" in out

def test_trytake_and_villain(game, capsys):
    villain = make_obj("badguy", villain=True, trytake=True)
    game.rooms["TEST"].objects.append(villain)
    game.parse_command("attack badguy")
    out = capsys.readouterr().out
    assert "resist" in out

def test_burning_and_flammable(game, capsys):
    paper = make_obj("paper", flammable=True)
    game.rooms["TEST"].objects.append(paper)
    game.parse_command("light paper")
    assert paper.attributes["burning"] is True
    game.parse_command("extinguish paper")
    assert paper.attributes["burning"] is False

def test_tieable_and_diggable(game, capsys):
    rope = make_obj("rope", tieable=True)
    dirt = make_obj("dirt", diggable=True)
    game.rooms["TEST"].objects.extend([rope, dirt])
    game.parse_command("tie rope")
    assert rope.attributes["tied"] is True
    game.parse_command("dig dirt")
    assert dirt.attributes["dug"] is True

def test_sacred_dangerous_collective(game, capsys):
    sacred = make_obj("idol", sacred=True)
    dangerous = make_obj("acid", dangerous=True)
    collective = make_obj("pile", collective=True)
    game.rooms["TEST"].objects.extend([sacred, dangerous, collective])
    game.parse_command("take idol")
    game.parse_command("take acid")
    game.parse_command("take pile")
    out = capsys.readouterr().out
    assert "invisible force" in out
    assert "dangerous" in out
    assert "as a whole" in out

def test_indescribable_asleep_searchable(game, capsys):
    indes = make_obj("mystery", indescribable=True)
    sleeper = make_obj("cat", asleep=True)
    searchy = make_obj("rock", searchable=True)
    game.rooms["TEST"].objects.extend([indes, sleeper, searchy])
    game.parse_command("examine mystery")
    game.parse_command("wake cat")
    game.parse_command("sleep cat")
    game.parse_command("search rock")
    out = capsys.readouterr().out
    assert "can't make out" in out
    assert "wake the cat" in out
    assert "put the cat to sleep" in out
    assert "find nothing of interest" in out

def test_openable_locked_transparent_bunch(game, capsys):
    door = make_obj("door", openable=True, locked=True)
    glass = make_obj("glass", transparent=True)
    bunch = make_obj("herd", bunch=True)
    game.rooms["TEST"].objects.extend([door, glass, bunch])
    game.parse_command("open door")
    game.parse_command("unlock door")
    game.parse_command("open door")
    game.parse_command("close door")
    game.parse_command("lock door")
    game.parse_command("look through glass")
    game.parse_command("take all")
    out = capsys.readouterr().out
    assert "locked" in out
    assert "unlock the door" in out
    assert "open the door" in out
    assert "close the door" in out
    assert "lock the door" in out
    assert "look through the glass" in out
    assert "as a whole" in out
