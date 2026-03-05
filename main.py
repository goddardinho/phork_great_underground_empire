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
    
    args = parser.parse_args()
    
    print("Welcome to Zork!")
    print("==================")
    
    if args.mud:
        print("Loading from original 1978 MIT Zork source files...")
    else:
        print("Using simple test world...")
    
    print()
    
    game = GameEngine(use_mud_files=args.mud, mud_directory=args.mud_dir)
    game.run()


if __name__ == "__main__":
    main()