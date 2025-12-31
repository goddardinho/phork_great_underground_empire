import sys
import io
from main import Game

def test_multiple_deaths():
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = io.StringIO("look\nlook\nlook\nlook\nlook\nlook\nlook\nlook\nlook\nquit\n")
    sys.stdout = output = io.StringIO()
    try:
        game = Game()
        # Force current room to be dark
        game.rooms[game.current_room].flags.append("dark")
        game.inventory = []  # No lantern
        # Die three times by grue
        for _ in range(9):
            game.parse_command("look")
        output_value = output.getvalue()
        assert "You have died" in output_value, "First death message missing!"
        assert "You feel strangely disoriented" in output_value, "Respawn message missing!"
        assert "Your adventure is over" in output_value, "Third death (game over) message missing!"
        print("Test passed: Multiple deaths trigger correct Zork-like behavior.")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"Test failed with exception: {e}")
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout

if __name__ == "__main__":
    test_multiple_deaths()
