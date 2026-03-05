#!/usr/bin/env python3
"""
Zork Rewrite - Main Entry Point

A clean, modern implementation of the classic Zork I text adventure game.
"""

from src.game import GameEngine


def main() -> None:
    """Main entry point for the game."""
    print("Welcome to Zork!")
    print("==================")
    print()
    
    game = GameEngine()
    game.run()


if __name__ == "__main__":
    main()