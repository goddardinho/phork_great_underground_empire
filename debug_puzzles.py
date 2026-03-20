#!/usr/bin/env python3

"""Debug puzzle integration"""

from src.game import GameEngine

def debug_puzzle_system():
    print("=== DEBUGGING PUZZLE SYSTEM ===")
    
    # Create game
    game = GameEngine()
    
    # Move to SHOUS where mailbox is
    game.player.move_to_room('SHOUS')
    print(f"Player in room: {game.player.current_room}")
    
    # Check puzzle manager
    has_pm = hasattr(game, 'puzzle_manager') and game.puzzle_manager is not None
    print(f"Has puzzle manager: {has_pm}")
    
    if game.puzzle_manager:
        print(f"Number of puzzles: {len(game.puzzle_manager.puzzles)}")
        
        for puzzle_id, puzzle in game.puzzle_manager.puzzles.items():
            print(f"  Puzzle: {puzzle_id} -> {puzzle.name} (state: {puzzle.state})")
    
        # Check mailbox puzzle
        mailbox_puzzle = game.puzzle_manager.get_puzzle('mailbox_tutorial')
        if mailbox_puzzle:
            print(f"Mailbox puzzle found - state: {mailbox_puzzle.state}, step: {mailbox_puzzle.current_step}")
            
            step = mailbox_puzzle.get_current_step()
            if step:
                print(f"Current step: {step.id}")
                
                # Test trigger
                try:
                    can_trigger = step.trigger_condition(
                        game=game,
                        command_verb='open',
                        target_object='mailbox'
                    )
                    print(f"Can trigger: {can_trigger}")
                except Exception as e:
                    print(f"Trigger error: {e}")
        else:
            print("No mailbox puzzle found!")
    
    print("\n=== TESTING COMMAND ===")
    game._process_command('open mailbox')
    
    # Check if state changed
    if game.puzzle_manager:
        mailbox_puzzle = game.puzzle_manager.get_puzzle('mailbox_tutorial')
        if mailbox_puzzle:
            print(f"After command - state: {mailbox_puzzle.state}, step: {mailbox_puzzle.current_step}")

if __name__ == '__main__':
    debug_puzzle_system()