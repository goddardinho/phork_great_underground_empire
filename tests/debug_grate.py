#!/usr/bin/env python3

"""Debug grate puzzle"""

from src.game import GameEngine

def debug_grate_puzzle():
    print("=== DEBUGGING GRATE PUZZLE ===")
    
    # Create game
    game = GameEngine()
    
    # Check grate puzzle
    grate_puzzle = game.puzzle_manager.get_puzzle('grate_unlock')
    if grate_puzzle:
        print(f"Grate puzzle found - state: {grate_puzzle.state}, step: {grate_puzzle.current_step}")
        
        # Move to NHOUS where keys should be  
        game.player.move_to_room('NHOUS')
        print(f"Player in room: {game.player.current_room}")
        
        step = grate_puzzle.get_current_step()
        if step:
            print(f"Current step: {step.id}")
            
            # Test trigger for "take keys"
            try:
                can_trigger = step.trigger_condition(
                    game=game,
                    command_verb='take',
                    target_object='keys'
                )
                print(f"Can trigger 'take keys': {can_trigger}")
            except Exception as e:
                print(f"Trigger error: {e}")
        
        print(f"Before take - step: {grate_puzzle.current_step}")
        game._process_command('take keys')
        print(f"After take - step: {grate_puzzle.current_step}")
        print(f"Player inventory: {game.player.inventory}")
        

if __name__ == '__main__':
    debug_grate_puzzle()