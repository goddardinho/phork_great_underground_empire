#!/usr/bin/env python3
"""
Performance Testing for World Navigation
Stress testing and performance analysis of world connectivity
"""

import sys
from pathlib import Path
import time
import statistics
import gc
from typing import List, Dict, Tuple
from collections import deque
import random

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game import GameEngine


class PerformanceTester:
    """Performance testing for world connectivity and navigation."""
    
    def __init__(self, game: GameEngine):
        self.game = game
        self.world = game.world
        
    def test_traversal_performance(self, iterations: int = 5) -> Dict[str, float]:
        """Test performance of world traversal multiple times."""
        
        print(f"⚡ Testing Traversal Performance ({iterations} iterations)...")
        
        times = []
        rooms_visited = []
        
        for i in range(iterations):
            print(f"   Run {i+1}/{iterations}...", end=" ")
            
            # Force garbage collection before each test
            gc.collect()
            
            start_time = time.time()
            visited = self._single_traversal("WHOUS")
            elapsed = time.time() - start_time
            
            times.append(elapsed)
            rooms_visited.append(len(visited))
            
            print(f"{elapsed:.3f}s ({len(visited)} rooms)")
        
        # Calculate statistics
        stats = {
            "mean_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0.0,
            "min_time": min(times),
            "max_time": max(times),
            "mean_rooms": statistics.mean(rooms_visited),
            "rooms_per_second": statistics.mean(rooms_visited) / statistics.mean(times)
        }
        
        print(f"\n📊 Performance Statistics:")
        print(f"   Mean time:        {stats['mean_time']:.3f}s ± {stats['std_dev']:.3f}s")
        print(f"   Range:            {stats['min_time']:.3f}s - {stats['max_time']:.3f}s")
        print(f"   Rooms/second:     {stats['rooms_per_second']:.1f}")
        print(f"   Rooms visited:    {stats['mean_rooms']:.1f}")
        
        return stats
    
    def _single_traversal(self, start_room: str) -> set:
        """Perform a single world traversal."""
        
        visited = set()
        queue = deque([start_room])
        
        while queue:
            room_id = queue.popleft()
            
            if room_id in visited:
                continue
                
            room = self.world.get_room(room_id)
            if not room:
                continue
                
            visited.add(room_id)
            
            for target in room.exits.values():
                if target not in visited and target in self.world.rooms:
                    queue.append(target)
        
        return visited
    
    def test_random_pathfinding(self, num_tests: int = 20) -> Dict[str, float]:
        """Test performance of pathfinding between random room pairs."""
        
        print(f"\n🎯 Testing Random Pathfinding ({num_tests} tests)...")
        
        room_ids = list(self.world.rooms.keys())
        times = []
        successful_paths = 0
        path_lengths = []
        
        for i in range(num_tests):
            # Pick two random rooms
            start = random.choice(room_ids)
            target = random.choice(room_ids)
            
            print(f"   Test {i+1:2d}: {start} → {target}...", end=" ")
            
            start_time = time.time()
            path = self._find_path(start, target)
            elapsed = time.time() - start_time
            
            times.append(elapsed)
            
            if path is not None:
                successful_paths += 1
                path_lengths.append(len(path))
                print(f"{elapsed:.4f}s (path: {len(path)} steps)")
            else:
                print(f"{elapsed:.4f}s (no path)")
        
        stats = {
            "mean_time": statistics.mean(times),
            "success_rate": successful_paths / num_tests,
            "mean_path_length": statistics.mean(path_lengths) if path_lengths else 0,
            "pathfinding_speed": 1.0 / statistics.mean(times)  # paths per second
        }
        
        print(f"\n📊 Pathfinding Statistics:")
        print(f"   Mean time:        {stats['mean_time']:.4f}s")
        print(f"   Success rate:     {stats['success_rate']:.1%}")
        print(f"   Mean path length: {stats['mean_path_length']:.1f} steps")
        print(f"   Paths/second:     {stats['pathfinding_speed']:.1f}")
        
        return stats
    
    def _find_path(self, start: str, target: str) -> List[str]:
        """Find path between two rooms using BFS."""
        
        if start == target:
            return []
            
        queue = deque([(start, [])])
        visited = set()
        
        while queue:
            current, path = queue.popleft()
            
            if current == target:
                return path
                
            if current in visited:
                continue
                
            visited.add(current)
            room = self.world.get_room(current)
            
            if room:
                for direction, next_room in room.exits.items():
                    if next_room not in visited and next_room in self.world.rooms:
                        queue.append((next_room, path + [direction]))
        
        return None  # No path found
    
    def test_memory_usage(self) -> Dict[str, int]:
        """Test memory usage during traversal."""
        
        print(f"\n🧠 Testing Memory Usage...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Get baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss
        
        print(f"   Baseline memory: {baseline_memory / 1024 / 1024:.1f} MB")
        
        # Perform traversal
        start_time = time.time()
        visited = self._single_traversal("WHOUS")
        elapsed = time.time() - start_time
        
        # Get peak memory
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - baseline_memory
        
        print(f"   Peak memory:     {peak_memory / 1024 / 1024:.1f} MB")
        print(f"   Memory increase: {memory_increase / 1024 / 1024:.1f} MB")
        print(f"   Memory per room: {memory_increase / len(visited):.0f} bytes")
        
        stats = {
            "baseline_memory_mb": baseline_memory / 1024 / 1024,
            "peak_memory_mb": peak_memory / 1024 / 1024,
            "memory_increase_mb": memory_increase / 1024 / 1024,
            "memory_per_room_bytes": memory_increase / len(visited) if len(visited) > 0 else 0
        }
        
        return stats
    
    def test_large_scale_navigation(self, navigations: int = 100) -> Dict[str, float]:
        """Test performance of many sequential navigation operations."""
        
        print(f"\n🗺️  Testing Large-Scale Navigation ({navigations} moves)...")
        
        room_ids = list(self.world.rooms.keys())
        times = []
        successful_moves = 0
        
        # Start at West of House
        current_room = "WHOUS"
        
        for i in range(navigations):
            room = self.world.get_room(current_room)
            if not room or not room.exits:
                # Pick a random room with exits
                candidates = [rid for rid in room_ids if self.world.get_room(rid).exits]
                current_room = random.choice(candidates)
                room = self.world.get_room(current_room)
            
            # Try to move in a random direction
            direction = random.choice(list(room.exits.keys()))
            target_room = room.exits[direction]
            
            start_time = time.time()
            
            # Simulate the navigation (just check if target exists)
            if target_room in self.world.rooms:
                current_room = target_room
                successful_moves += 1
            
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            if (i + 1) % 20 == 0:
                print(f"   Progress: {i+1}/{navigations} moves...")
        
        stats = {
            "total_time": sum(times),
            "mean_move_time": statistics.mean(times),
            "moves_per_second": len(times) / sum(times),
            "success_rate": successful_moves / navigations
        }
        
        print(f"\n📊 Large-Scale Navigation:")
        print(f"   Total time:       {stats['total_time']:.3f}s")
        print(f"   Mean move time:   {stats['mean_move_time']:.6f}s")
        print(f"   Moves/second:     {stats['moves_per_second']:.1f}")
        print(f"   Success rate:     {stats['success_rate']:.1%}")
        
        return stats
    
    def run_stress_test(self) -> Dict[str, any]:
        """Run comprehensive stress test of the navigation system."""
        
        print("🔥 NAVIGATION STRESS TEST")
        print("=" * 50)
        
        results = {}
        
        # Test 1: Traversal Performance
        results["traversal"] = self.test_traversal_performance(iterations=5)
        
        # Test 2: Random Pathfinding  
        results["pathfinding"] = self.test_random_pathfinding(num_tests=25)
        
        # Test 3: Memory Usage
        try:
            results["memory"] = self.test_memory_usage()
        except ImportError:
            print("   ⚠️  psutil not available, skipping memory test")
            results["memory"] = None
        
        # Test 4: Large-Scale Navigation
        results["large_scale"] = self.test_large_scale_navigation(navigations=200)
        
        # Overall assessment
        print(f"\n🏆 STRESS TEST SUMMARY")
        print(f"   Traversal speed:  {results['traversal']['rooms_per_second']:.1f} rooms/sec")
        print(f"   Pathfinding:      {results['pathfinding']['pathfinding_speed']:.1f} paths/sec")
        print(f"   Navigation speed: {results['large_scale']['moves_per_second']:.1f} moves/sec")
        
        # Performance assessment
        traversal_speed = results['traversal']['rooms_per_second']
        if traversal_speed > 1000:
            print(f"   ✅ EXCELLENT performance")
        elif traversal_speed > 500:
            print(f"   ⚠️  GOOD performance")
        else:
            print(f"   ❌ POOR performance - optimization needed")
        
        return results


def main():
    """Run performance testing suite."""
    
    print("⚡ ZORK WORLD PERFORMANCE TESTING")
    print("=" * 50)
    
    # Load game world
    print("📚 Loading world...")
    game = GameEngine(use_mud_files=True)
    
    if not game.world.rooms:
        print("❌ No rooms loaded!")
        return False
        
    print(f"✅ Loaded {len(game.world.rooms)} rooms")
    
    # Run performance tests
    tester = PerformanceTester(game)
    results = tester.run_stress_test()
    
    # Save results (optional)
    import json
    results_file = Path(__file__).parent / "performance_test_results.json"
    
    # Convert any non-serializable values
    serializable_results = {}
    for key, value in results.items():
        if value is not None:
            serializable_results[key] = value
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Return success based on performance
    traversal_speed = results['traversal']['rooms_per_second']
    return traversal_speed > 100  # Minimum acceptable performance


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)