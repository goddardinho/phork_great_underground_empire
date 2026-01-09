import io
import sys
import builtins
import pytest
from main import Game

def test_help_command_output(capsys):
    game = Game()
    # Simulate entering the 'help' command
    game.parse_command('help')
    captured = capsys.readouterr()
    output = captured.out
    # Check for key help output features
    assert "Available Commands:" in output
    assert "look" in output
    assert "inventory" in output
    assert "Usage:" in output
    assert "help" in output
    assert "quit" in output
    # Check that at least one usage example is present
    assert "Usage:" in output
    # Check that the help message is not empty
    assert len(output.strip()) > 0
