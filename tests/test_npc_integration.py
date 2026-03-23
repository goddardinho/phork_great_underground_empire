#!/usr/bin/env python3
"""Quick test of NPC integration in the actual game."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.game import GameEngine


def test_npc_integration():
    """Test NPC system in the actual game."""
    print("Testing NPC system integration...")
    
    # Create game engine
    game = GameEngine(debug_mode=True)
    
    # Check that NPCs were created
    print("\nNPCs in West of House:")
    npcs = game.npc_manager.get_npcs_in_room("WHOUS")
    for npc in npcs:
        print(f"  - {npc.name}: {npc.description}")
    
    # Test looking around (should show NPCs)
    print("\n" + "="*50)
    print("TESTING: look command (should show NPCs)")
    print("="*50)
    game._look_around()
    
    # Test talking to hermit
    print("\n" + "="*50)
    print("TESTING: talk hermit")
    print("="*50)
    from src.parser.command_parser import Command
    talk_command = Command("talk", "hermit")
    game._handle_talk(talk_command)
    
    # Test asking about treasure
    print("\n" + "="*50)
    print("TESTING: ask hermit about treasure")  
    print("="*50)
    ask_command = Command("ask", "hermit", preposition="about", noun2="treasure")
    game._handle_ask(ask_command)
    
    # Test greeting
    print("\n" + "="*50)
    print("TESTING: greet oracle")
    print("="*50)
    greet_command = Command("greet", "oracle")
    game._handle_greet(greet_command)
    
    # Test saying something
    print("\n" + "="*50)
    print("TESTING: say \"Hello everyone!\"")
    print("="*50)
    say_command = Command("say")  # say command uses different processing
    game._handle_say(say_command, "say \"Hello everyone!\"")
    
    print("\n" + "="*50)
    print("NPC INTEGRATION TEST COMPLETE")
    print("="*50)
    print("\nReady to play! Start the game normally and try:")
    print("  look")
    print("  talk hermit")
    print("  ask oracle about treasure")
    print("  greet hermit")
    print("  say \"hello\"")


if __name__ == "__main__":
    test_npc_integration()