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
        "--test", 
        action="store_true", 
        help="Use simple test world instead of full Zork experience"
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
    parser.add_argument(
        "--debug",
        action="store_true", 
        help="Show detailed loading and parsing information"
    )
    
    args = parser.parse_args()
    
    # Only show loading messages in debug mode
    if args.debug:
        print("Welcome to Zork!")
        print("==================")
        if args.test:
            print("Using simple test world...")
        else:
            print("Loading from original 1978 MIT Zork source files...")
        print()
    else:
        # Show fun loading indicator for normal users
        if not args.test:
            print("Welcome to Zork!")
            print("Waking up the grues and dusting off the treasure...")
    
    if args.demo_disambiguation:
        if args.debug:
            print("Running disambiguation demo...")
        else:
            print("Welcome to Zork!")
            print("Running disambiguation demo...")
        print()
        demo_disambiguation()
        return
    
    game = GameEngine(use_mud_files=not args.test, mud_directory=args.mud_dir, debug_mode=args.debug)
    game.run()


def demo_disambiguation() -> None:
    """Run a quick demonstration of the disambiguation system."""
    from src.game import GameEngine
    
    print("This demo shows the ambiguity resolution system.")
    print("When multiple objects match your command, the game will")
    print("ask you to choose which one you mean.\n")
    
    game = GameEngine(use_mud_files=False, debug_mode=True)  # Use debug mode for demo
    
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