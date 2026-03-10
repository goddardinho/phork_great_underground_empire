#!/usr/bin/env python3
"""
Full Connectivity Testing System
Automated traversal and validation of the entire Zork game world
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import deque, defaultdict
import json
import time
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game import GameEngine
from src.world.room import Room
from src.world.world import World


@dataclass
class TraversalStats:
    """Statistics from world traversal."""
    total_rooms: int = 0
    reachable_rooms: int = 0
    unreachable_rooms: int = 0
    total_exits: int = 0
    working_exits: int = 0
    broken_exits: int = 0
    traversal_time: float = 0.0
    max_depth: int = 0
    paths_found: int = 0


@dataclass  
class RoomInfo:
    """Information about a room discovered during traversal."""
    id: str
    name: str
    depth: int
    visited_from: Optional[str]
    direction_taken: Optional[str]
    exits: Dict[str, str]
    flags: int
    items: List[str]
    reachable: bool = True


class ConnectivityTester:
    """Comprehensive connectivity testing for the Zork world."""
    
    def __init__(self, game: GameEngine):
        self.game = game
        self.world = game.world
        self.visited_rooms: Set[str] = set()
        self.room_info: Dict[str, RoomInfo] = {}
        self.exit_errors: List[Tuple[str, str, str]] = []
        self.unreachable_rooms: Set[str] = set()
        self.room_paths: Dict[str, List[str]] = {}
        self.stats = TraversalStats()
        
    def test_full_connectivity(self, start_room: str = "WHOUS") -> TraversalStats:
        """
        Test full world connectivity starting from given room.
        Performs breadth-first traversal to discover all reachable areas.
        """
        print("🔍 Starting Full Connectivity Test...")
        print(f"📍 Starting location: {start_room}")
        print()
        
        start_time = time.time()
        
        # Initialize stats
        self.stats.total_rooms = len(self.world.rooms)
        
        # Perform breadth-first traversal 
        self._traverse_world(start_room)
        
        # Analyze unreachable rooms
        self._find_unreachable_rooms()
        
        # Validate all exits
        self._validate_all_exits()
        
        # Calculate final stats
        self.stats.traversal_time = time.time() - start_time
        self.stats.reachable_rooms = len(self.visited_rooms)
        self.stats.unreachable_rooms = len(self.unreachable_rooms)
        
        # Print results
        self._print_results()
        
        return self.stats
    
    def _traverse_world(self, start_room: str) -> None:
        """Perform breadth-first traversal of the world."""
        
        if start_room not in self.world.rooms:
            raise ValueError(f"Start room {start_room} not found in world")
        
        queue = deque([(start_room, 0, None, None)])  # room_id, depth, from_room, direction
        
        while queue:
            room_id, depth, from_room, direction = queue.popleft()
            
            if room_id in self.visited_rooms:
                continue
                
            room = self.world.get_room(room_id)
            if not room:
                self.exit_errors.append((from_room or "UNKNOWN", direction or "UNKNOWN", room_id))
                continue
            
            # Mark as visited and record info
            self.visited_rooms.add(room_id)
            self.room_info[room_id] = RoomInfo(
                id=room_id,
                name=room.name,
                depth=depth,
                visited_from=from_room,
                direction_taken=direction,
                exits=room.exits.copy(),
                flags=room.flags,
                items=room.items.copy() if hasattr(room, 'items') else []
            )
            
            # Record path to this room
            if from_room and from_room in self.room_paths:
                self.room_paths[room_id] = self.room_paths[from_room] + [direction or "unknown"]
            else:
                self.room_paths[room_id] = []
            
            # Update max depth
            self.stats.max_depth = max(self.stats.max_depth, depth)
            
            # Add all exits to queue for exploration
            for exit_dir, target_room in room.exits.items():
                if target_room not in self.visited_rooms:
                    queue.append((target_room, depth + 1, room_id, exit_dir))
                    
            # Progress indicator
            if len(self.visited_rooms) % 10 == 0:
                print(f"📍 Explored {len(self.visited_rooms)} rooms... (depth {depth})")
    
    def _find_unreachable_rooms(self) -> None:
        """Identify rooms that weren't reached during traversal."""
        
        all_rooms = set(self.world.rooms.keys())
        self.unreachable_rooms = all_rooms - self.visited_rooms
        
        # Add unreachable room info
        for room_id in self.unreachable_rooms:
            room = self.world.get_room(room_id)
            if room:
                self.room_info[room_id] = RoomInfo(
                    id=room_id,
                    name=room.name,
                    depth=-1,  # Unreachable
                    visited_from=None,
                    direction_taken=None,
                    exits=room.exits.copy(),
                    flags=room.flags,
                    items=room.items.copy() if hasattr(room, 'items') else [],
                    reachable=False
                )
    
    def _validate_all_exits(self) -> None:
        """Validate all exits point to existing rooms."""
        
        self.stats.total_exits = 0
        self.stats.working_exits = 0
        self.stats.broken_exits = 0
        
        for room_id, room in self.world.rooms.items():
            for direction, target_id in room.exits.items():
                self.stats.total_exits += 1
                
                if target_id in self.world.rooms:
                    self.stats.working_exits += 1
                else:
                    self.stats.broken_exits += 1
                    self.exit_errors.append((room_id, direction, target_id))
    
    def _print_results(self) -> None:
        """Print comprehensive test results."""
        
        print("\n" + "="*60)
        print("🔍 FULL CONNECTIVITY TEST RESULTS")
        print("="*60)
        
        # Overall Statistics
        print(f"\n📊 **WORLD STATISTICS**")
        print(f"   Total Rooms:      {self.stats.total_rooms}")
        print(f"   Reachable:        {self.stats.reachable_rooms} ({self.stats.reachable_rooms/self.stats.total_rooms*100:.1f}%)")
        print(f"   Unreachable:      {self.stats.unreachable_rooms} ({self.stats.unreachable_rooms/self.stats.total_rooms*100:.1f}%)")
        print(f"   Max Depth:        {self.stats.max_depth}")
        print(f"   Traversal Time:   {self.stats.traversal_time:.2f}s")
        
        print(f"\n🚪 **EXIT ANALYSIS**")  
        print(f"   Total Exits:      {self.stats.total_exits}")
        print(f"   Working Exits:    {self.stats.working_exits} ({self.stats.working_exits/self.stats.total_exits*100:.1f}%)")
        print(f"   Broken Exits:     {self.stats.broken_exits} ({self.stats.broken_exits/self.stats.total_exits*100:.1f}%)")
        
        # Reachability Summary
        if self.stats.reachable_rooms > 0:
            reach_percentage = (self.stats.reachable_rooms / self.stats.total_rooms) * 100
            if reach_percentage >= 90:
                print(f"\n✅ **EXCELLENT CONNECTIVITY** ({reach_percentage:.1f}%)")
            elif reach_percentage >= 75:
                print(f"\n⚠️  **GOOD CONNECTIVITY** ({reach_percentage:.1f}%)")
            else:
                print(f"\n❌ **POOR CONNECTIVITY** ({reach_percentage:.1f}%)")
        
        # Show broken exits
        if self.exit_errors:
            print(f"\n🚨 **BROKEN EXITS** ({len(self.exit_errors)} found):")
            for room_id, direction, target in self.exit_errors[:10]:  # Show first 10
                print(f"   {room_id} --{direction}--> {target} (MISSING)")
            if len(self.exit_errors) > 10:
                print(f"   ... and {len(self.exit_errors) - 10} more")
        
        # Show some unreachable rooms
        if self.unreachable_rooms:
            print(f"\n🚫 **UNREACHABLE ROOMS** ({len(self.unreachable_rooms)} found):")
            unreachable_list = list(self.unreachable_rooms)[:10]
            for room_id in unreachable_list:
                room_info = self.room_info[room_id]
                print(f"   {room_id}: {room_info.name}")
            if len(self.unreachable_rooms) > 10:
                print(f"   ... and {len(self.unreachable_rooms) - 10} more")
        
        # Performance indicators
        rooms_per_second = self.stats.reachable_rooms / self.stats.traversal_time if self.stats.traversal_time > 0 else 0
        print(f"\n⚡ **PERFORMANCE**")
        print(f"   Rooms/second:     {rooms_per_second:.1f}")
        print(f"   Average depth:    {sum(info.depth for info in self.room_info.values() if info.depth >= 0) / self.stats.reachable_rooms:.1f}")
    
    def generate_connectivity_map(self) -> Dict[str, Any]:
        """Generate a detailed connectivity map for analysis."""
        
        connectivity_map = {
            "metadata": {
                "timestamp": time.time(),
                "total_rooms": self.stats.total_rooms,
                "reachable_rooms": self.stats.reachable_rooms,
                "traversal_time": self.stats.traversal_time
            },
            "reachable_rooms": {},
            "unreachable_rooms": [],
            "broken_exits": [],
            "depth_analysis": defaultdict(int)
        }
        
        # Add reachable room details
        for room_id in list(self.visited_rooms):  # Convert set to list
            room_info = self.room_info[room_id]
            connectivity_map["reachable_rooms"][room_id] = {
                "name": room_info.name,
                "depth": room_info.depth,
                "visited_from": room_info.visited_from,
                "direction_taken": room_info.direction_taken,
                "exits": room_info.exits,
                "path_length": len(self.room_paths.get(room_id, []))
            }
            connectivity_map["depth_analysis"][room_info.depth] += 1
        
        # Add unreachable rooms
        connectivity_map["unreachable_rooms"] = [
            {
                "id": room_id,
                "name": self.room_info[room_id].name,
                "exits": self.room_info[room_id].exits
            }
            for room_id in list(self.unreachable_rooms)  # Convert set to list
        ]
        
        # Add broken exits
        connectivity_map["broken_exits"] = [
            {
                "from_room": room_id,
                "direction": direction,
                "target_room": target
            }
            for room_id, direction, target in self.exit_errors
        ]
        
        return connectivity_map
    
    def save_connectivity_report(self, filename: str = "connectivity_report.json") -> None:
        """Save detailed connectivity report to JSON file."""
        
        report = {
            "test_timestamp": time.time(), 
            "statistics": {
                "total_rooms": self.stats.total_rooms,
                "reachable_rooms": self.stats.reachable_rooms,
                "unreachable_rooms": self.stats.unreachable_rooms,
                "total_exits": self.stats.total_exits,
                "working_exits": self.stats.working_exits,
                "broken_exits": self.stats.broken_exits,
                "max_depth": self.stats.max_depth,
                "traversal_time": self.stats.traversal_time
            },
            "connectivity_map": self.generate_connectivity_map(),
            "room_details": {
                room_id: {
                    "name": info.name,
                    "depth": info.depth,
                    "reachable": info.reachable,
                    "visited_from": info.visited_from,
                    "direction_taken": info.direction_taken,
                    "exits": info.exits,
                    "flags": info.flags,
                    "items": info.items,
                    "path_to_room": self.room_paths.get(room_id, [])
                }
                for room_id, info in self.room_info.items()
            }
        }
        
        filepath = Path(__file__).parent / filename
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {filepath}")
        return filepath


def test_pathfinding(game: GameEngine, start: str, target: str) -> Optional[List[str]]:
    """
    Test pathfinding between two specific rooms.
    Returns path as list of directions, or None if no path exists.
    """
    print(f"\n🗺️  **PATHFINDING TEST**: {start} → {target}")
    
    if start not in game.world.rooms:
        print(f"❌ Start room {start} not found")
        return None
        
    if target not in game.world.rooms:
        print(f"❌ Target room {target} not found")
        return None
    
    # BFS pathfinding
    queue = deque([(start, [])])
    visited = set()
    
    while queue:
        current_room, path = queue.popleft()
        
        if current_room == target:
            print(f"✅ Path found! Length: {len(path)} steps")
            if path:
                print(f"   Directions: {' → '.join(path)}")
            else:
                print(f"   (Start and target are the same room)")
            return path
            
        if current_room in visited:
            continue
            
        visited.add(current_room)
        room = game.world.get_room(current_room)
        
        if room:
            for direction, next_room in room.exits.items():
                if next_room not in visited and next_room in game.world.rooms:
                    queue.append((next_room, path + [direction]))
    
    print(f"❌ No path found between {start} and {target}")
    return None


def main():
    """Run comprehensive connectivity tests."""
    print("🏰 Zork World Connectivity Testing System")
    print("=" * 50)
    
    # Load the game world
    print("📚 Loading Zork world...")
    game = GameEngine(use_mud_files=True)
    
    if not game.world.rooms:
        print("❌ No rooms loaded! Make sure .mud files are available.")
        return
        
    print(f"✅ Loaded {len(game.world.rooms)} rooms")
    
    # Create connectivity tester
    tester = ConnectivityTester(game)
    
    # Run full connectivity test
    stats = tester.test_full_connectivity()
    
    # Save detailed report
    report_path = tester.save_connectivity_report("connectivity_test_report.json")
    
    # Test some specific pathfinding
    print(f"\n🗺️  **PATHFINDING TESTS**")
    test_pathfinding(game, "WHOUS", "TREAS")  # West of House to Treasure Room
    test_pathfinding(game, "WHOUS", "MTREE")  # West of House to Up a Tree  
    test_pathfinding(game, "TREAS", "TEMP")   # Treasure Room to Temple
    
    # Final summary
    print(f"\n🎯 **CONNECTIVITY TEST COMPLETE**")
    print(f"   Reachability: {stats.reachable_rooms}/{stats.total_rooms} rooms ({stats.reachable_rooms/stats.total_rooms*100:.1f}%)")
    print(f"   Exit Success: {stats.working_exits}/{stats.total_exits} exits ({stats.working_exits/stats.total_exits*100:.1f}%)")
    print(f"   Report saved: {report_path}")
    
    # Return success/failure based on connectivity
    return stats.reachable_rooms / stats.total_rooms >= 0.8  # 80% reachability threshold


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)