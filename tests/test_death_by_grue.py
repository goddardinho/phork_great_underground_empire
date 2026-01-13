import sys
import io
from main import Game

def test_death_by_grue():
    # Redirect stdin and stdout
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = io.StringIO("look\nlook\nlook\nquit\n")  # Simulate enough actions to trigger grue
    sys.stdout = output = io.StringIO()
    result_message = ""
    try:
        game = Game()
        # Force current room to be dark (support both bitmask and list flags)
        room = game.rooms[game.current_room]
        if hasattr(room, 'set_flag'):
            room.set_flag(getattr(room, 'ROOM_DARK', 0x01))
        elif isinstance(room.flags, list):
            if 'dark' not in room.flags:
                room.flags.append('dark')
        elif isinstance(room.flags, int):
            room.flags |= 0x01  # fallback if set_flag missing
        game.inventory = []  # No lantern
        # Perform actions to trigger grue
        for _ in range(3):
            game.parse_command("look")
        # Check output for death message
        output_value = output.getvalue()
        if "You have died" in output_value and ("restart" in output_value.lower() or "quit" in output_value.lower()):
            result_message = "Test passed: Death by grue triggers game over and prompt."
        else:
            result_message = "Test failed: Output did not contain expected death message or prompt."
            result_message += "\nOutput was:\n" + output_value
    except AssertionError as e:
        result_message = f"Test failed with assertion error: {e}"
    except Exception as e:
        result_message = f"Test failed with exception: {e}"
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
        print(result_message)

if __name__ == "__main__":
    test_death_by_grue()
