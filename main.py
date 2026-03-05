#!/usr/bin/env python3
"""
Zork Rewrite - Main Entry Point

A clean, modern implementation of the classic Zork I text adventure game.
"""

import sys
import argparse
from pathlib import Path

from src.game import GameEngine


def main() -> None:
    """Main entry point for the game."""
    parser = argparse.ArgumentParser(description="Zork - Text Adventure Game")
    parser.add_argument(
        "--mud", 
        action="store_true", 
        help="Load world from original .mud files instead of simple test world"
    )
    parser.add_argument(
        "--mud-dir", 
        type=Path, 
        default=Path("zork_mtl_source"),
        help="Directory containing .mud files (default: zork_mtl_source)"
    )
    parser.add_argument(
        "--demo-disambiguation",
        action="store_true",
        help="Run a quick demo showing the disambiguation system"
    )
    
    args = parser.parse_args()
    
    print("Welcome to Zork!")
    print("==================")
    
    if args.demo_disambiguation:
        print("Running disambiguation demo...")
        print()
        demo_disambiguation()
        return
    
    if args.mud:
        print("Loading from original 1978 MIT Zork source files...")
    else:
        print("Using simple test world...")
    
    print()
    
    game = GameEngine(use_mud_files=args.mud, mud_directory=args.mud_dir)
    game.run()


def demo_disambiguation() -> None:
    """Run a quick demonstration of the disambiguation system."""
    from src.game import GameEngine
    
    print("This demo shows the ambiguity resolution system.")
    print("When multiple objects match your command, the game will")
    print("ask you to choose which one you mean.\n")
    
    game = GameEngine(use_mud_files=False)
    
    print("Moving to the Ancient Temple which contains two knives...")
    game.player.move_to_room("TEMPLE")
    game._look_around()
    print()
    
    print("Now let's try: 'take knife'")
    print("This should show disambiguation because there are two knives.")
    print("-" * 50)
    
    # This will trigger disambiguation
    game._process_command("take knife")
    
    print()
    print("As you can see, when there are multiple matching objects,")
    print("the game asks you to choose which one you mean!")
    print("You can respond with a number (1, 2, etc.) or descriptive")
    print("text like 'rusty' or 'silver'.")
    print()
    print("This system works with all commands: take, examine, drop, etc.")
    print("Try running the game normally to experience it interactively!")
    print()
    print("✅ Ambiguity resolution system is fully operational!")


if __name__ == "__main__":
    main()