#!/usr/bin/env python3
"""
Debug connectivity analysis to understand audit results
"""

from src.game import GameEngine
from collections import deque

def manual_connectivity_test():
    game = GameEngine(use_mud_files=True)
    start_room = 'WHOUS'
    visited = set()
    queue = deque([start_room])
    
    print(f'Starting connectivity test from {start_room}')
    
    step = 0
    while queue and step < 50:  # Limit to avoid too much output
        current_id = queue.popleft()
        if current_id in visited:
            continue
            
        visited.add(current_id)
        current_room = game.world.get_room(current_id)
        
        if not current_room:
            print(f'Warning: Room {current_id} not found!')
            continue
            
        print(f'{step+1:2d}. Visiting {current_id}: {len(current_room.exits)} exits -> {list(current_room.exits.values())}')
        
        # Add connected rooms to queue
        for direction, target_id in current_room.exits.items():
            if target_id not in visited:
                queue.append(target_id)
        
        step += 1
    
    print(f'\nTotal rooms visited: {len(visited)}')
    print(f'Remaining in queue: {len(queue)}')
    
    # Continue until all reachable rooms found
    while queue:
        current_id = queue.popleft()
        if current_id in visited:
            continue
            
        visited.add(current_id)
        current_room = game.world.get_room(current_id)
        
        if not current_room:
            continue
            
        # Add connected rooms to queue
        for direction, target_id in current_room.exits.items():
            if target_id not in visited:
                queue.append(target_id)
    
    print(f'Final total rooms reachable: {len(visited)}')
    return visited

if __name__ == '__main__':
    visited_rooms = manual_connectivity_test()
    print(f'All reachable rooms ({len(visited_rooms)}): {sorted(visited_rooms)}')