#!/usr/bin/env python3
"""
Connectivity Repair System
Fixes specific connectivity issues identified in the gap analysis
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game import GameEngine
from src.world.room import Room


class ConnectivityRepairer:
    """Repairs specific connectivity issues to improve world traversal."""
    
    def __init__(self, game: GameEngine):
        self.game = game
        self.world = game.world
        self.repairs_made = 0
        self.connections_added = []
        
    def apply_connectivity_fixes(self) -> Dict:
        """Apply targeted fixes for major connectivity issues."""
        
        print("🔧 APPLYING CONNECTIVITY FIXES")
        print("=" * 40)
        
        # Track repairs
        initial_reachable = self._count_reachable_rooms()
        
        # Apply specific fixes
        self._fix_boiler_room_connection()
        self._fix_grate_room_connections()
        self._fix_cellar_connections()
        self._fix_maze_entry_connections()
        self._fix_other_critical_connections()
        
        # Verify improvements
        final_reachable = self._count_reachable_rooms()
        improvement = final_reachable - initial_reachable
        
        results = {
            "repairs_made": self.repairs_made,
            "connections_added": len(self.connections_added),
            "initial_reachable": initial_reachable,
            "final_reachable": final_reachable,
            "improvement": improvement,
            "connectivity_rate": final_reachable / len(self.world.rooms) * 100
        }
        
        self._print_repair_results(results)
        return results
    
    def _count_reachable_rooms(self, start_room: str = "WHOUS") -> int:
        """Count reachable rooms from start position."""
        
        visited = set()
        queue = [start_room] 
        
        while queue:
            room_id = queue.pop(0)
            
            if room_id in visited:
                continue
                
            room = self.world.get_room(room_id)
            if not room:
                continue
                
            visited.add(room_id)
            
            for target in room.exits.values():
                if target not in visited and target in self.world.rooms:
                    queue.append(target)
        
        return len(visited)
    
    def _add_bidirectional_connection(self, room1_id: str, direction1: str, 
                                    room2_id: str, direction2: str) -> bool:
        """Add bidirectional connection between two rooms."""
        
        room1 = self.world.get_room(room1_id)
        room2 = self.world.get_room(room2_id)
        
        if not room1 or not room2:
            print(f"   ❌ Cannot connect {room1_id} and {room2_id} - rooms not found")
            return False
        
        # Check if connections already exist
        if room1.exits.get(direction1) == room2_id and room2.exits.get(direction2) == room1_id:
            print(f"   ✓ Connection {room1_id}<->{room2_id} already exists")
            return False
        
        # Add the connections
        changes_made = False
        
        if room1.exits.get(direction1) != room2_id:
            room1.exits[direction1] = room2_id
            changes_made = True
            print(f"   ➕ Added {room1_id} --{direction1}--> {room2_id}")
        
        if room2.exits.get(direction2) != room1_id:
            room2.exits[direction2] = room1_id
            changes_made = True
            print(f"   ➕ Added {room2_id} --{direction2}--> {room1_id}")
        
        if changes_made:
            self.repairs_made += 1
            self.connections_added.append((room1_id, direction1, room2_id, direction2))
        
        return changes_made
    
    def _fix_boiler_room_connection(self) -> None:
        """Fix the critical Boiler Room <-> Living Room connection."""
        
        print("\n🔧 Fixing Boiler Room Connection...")
        
        # BLROO has exit east to LROOM, but LROOM needs west back to BLROO
        self._add_bidirectional_connection("LROOM", "west", "BLROO", "east")
        
        # Also connect BLROO to the treasure room system via Cyclops room
        self._add_bidirectional_connection("CYCLO", "north", "BLROO", "south")
    
    def _fix_grate_room_connections(self) -> None:
        """Fix the Grate Room connections to Forest Clearing."""
        
        print("\n🔧 Fixing Grate Room Connection...")
        
        # MGRAT should connect up to CLEAR (Forest Clearing)
        # This is a key connection to the underground maze system
        self._add_bidirectional_connection("MGRAT", "up", "CLEAR", "down")
    
    def _fix_cellar_connections(self) -> None:
        """Fix various cellar and basement connections."""
        
        print("\n🔧 Fixing Cellar Connections...")
        
        # Connect CELLA (Cellar) to various underground areas
        # CHAS2 has west to CELLA, need east back from CELLA
        self._add_bidirectional_connection("CELLA", "east", "CHAS2", "west")
        
        # Add connection from CELLA down to troll area
        self._add_bidirectional_connection("CELLA", "south", "MTROL", "north")
    
    def _fix_maze_entry_connections(self) -> None:
        """Fix connections into the maze system."""
        
        print("\n🔧 Fixing Maze Entry Connections...")
        
        # Connect Troll Room to maze system 
        self._add_bidirectional_connection("MTROL", "east", "MAZE1", "west")
        
        # Connect Gallery to Cyclops room (treasure area access)
        self._add_bidirectional_connection("GALLE", "north", "CYCLO", "up")
    
    def _fix_other_critical_connections(self) -> None:
        """Fix other important connectivity gaps."""
        
        print("\n🔧 Fixing Other Critical Connections...")
        
        # Connect Rainbow Room to Pot of Gold
        self._add_bidirectional_connection("RAINB", "east", "POG", "west")
        
        # Connect Dam area to reservoir system
        self._add_bidirectional_connection("DAM", "south", "RESER", "north")
        
        # Connect some isolated temples and caves
        self._add_bidirectional_connection("TEMP1", "east", "TEMP2", "west")
        
        # Connect mines to the cave system
        self._add_bidirectional_connection("DOME", "west", "MINE1", "east")
    
    def _print_repair_results(self, results: Dict) -> None:
        """Print comprehensive repair results."""
        
        print(f"\n🔧 **CONNECTIVITY REPAIR RESULTS**")
        print(f"   Repairs made:       {results['repairs_made']}")
        print(f"   Connections added:  {results['connections_added']}")
        print(f"   Reachable rooms:    {results['initial_reachable']} → {results['final_reachable']}")
        print(f"   Improvement:        +{results['improvement']} rooms")
        print(f"   New connectivity:   {results['connectivity_rate']:.1f}%")
        
        if results['improvement'] > 50:
            print(f"   ✅ **EXCELLENT** improvement! Major connectivity restored.")
        elif results['improvement'] > 20:
            print(f"   ⚠️  **GOOD** improvement. Some areas now accessible.")
        elif results['improvement'] > 5:
            print(f"   ⚠️  **MINOR** improvement. More fixes needed.")
        else:
            print(f"   ❌ **NO IMPROVEMENT**. Manual inspection required.")
        
        # Show the connections that were added
        if self.connections_added:
            print(f"\n📋 **CONNECTIONS ADDED:**")
            for room1, dir1, room2, dir2 in self.connections_added[:10]:
                print(f"   {room1} <--{dir1}/{dir2}--> {room2}")
            if len(self.connections_added) > 10:
                print(f"   ... and {len(self.connections_added) - 10} more")
    
    def save_repair_log(self, filename: str = "connectivity_repairs.json") -> Path:
        """Save repair log for reference."""
        
        import json
        
        repair_log = {
            "timestamp": "2024-03-10", 
            "repairs_made": self.repairs_made,
            "connections_added": [
                {
                    "room1": room1,
                    "direction1": dir1, 
                    "room2": room2,
                    "direction2": dir2
                }
                for room1, dir1, room2, dir2 in self.connections_added
            ]
        }
        
        filepath = Path(__file__).parent / filename
        with open(filepath, 'w') as f:
            json.dump(repair_log, f, indent=2)
        
        print(f"\n📄 Repair log saved to: {filepath}")
        return filepath


def main():
    """Run connectivity repair system."""
    
    print("🔧 ZORK CONNECTIVITY REPAIR SYSTEM")
    print("=" * 50)
    
    # Load game world
    print("📚 Loading world...")
    game = GameEngine(use_mud_files=True)
    
    if not game.world.rooms:
        print("❌ No rooms loaded!")
        return False
    
    print(f"✅ Loaded {len(game.world.rooms)} rooms")
    
    # Run repairs
    repairer = ConnectivityRepairer(game)
    results = repairer.apply_connectivity_fixes()
    
    # Save repair log
    repairer.save_repair_log()
    
    # Test connectivity after repairs
    print(f"\n🧪 **POST-REPAIR CONNECTIVITY TEST**")
    from tests.quick_connectivity import quick_connectivity_check
    connectivity_good = quick_connectivity_check()
    
    print(f"\n🎯 **REPAIR SYSTEM COMPLETE**")
    print(f"   Final connectivity: {results['connectivity_rate']:.1f}%")
    print(f"   Improvement: +{results['improvement']} rooms")
    
    return results['connectivity_rate'] > 50  # 50% minimum acceptable


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)