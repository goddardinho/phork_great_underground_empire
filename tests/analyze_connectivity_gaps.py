#!/usr/bin/env python3
"""
Connectivity Gap Analyzer
Identifies missing connections and suggests fixes for world connectivity issues
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game import GameEngine


class ConnectivityGapAnalyzer:  
    """Analyzes connectivity gaps and suggests solutions."""
    
    def __init__(self, game: GameEngine):
        self.game = game
        self.world = game.world
        self.reachable_rooms = set()
        self.unreachable_rooms = set()
        self.potential_bridges = []
        self.missing_connections = []
        
    def analyze_connectivity_gaps(self, start_room: str = "WHOUS") -> Dict:
        """Analyze connectivity gaps and find potential solutions."""
        
        print("🔍 CONNECTIVITY GAP ANALYSIS")
        print("=" * 40)
        
        # Find reachable rooms
        self._find_reachable_rooms(start_room)
        
        # Identify unreachable clusters 
        unreachable_clusters = self._find_unreachable_clusters()
        
        # Find potential bridge connections
        self._find_potential_bridges()
        
        # Analyze exit patterns
        exit_analysis = self._analyze_exit_patterns()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(unreachable_clusters)
        
        results = {
            "reachable_count": len(self.reachable_rooms),
            "unreachable_count": len(self.unreachable_rooms), 
            "unreachable_clusters": unreachable_clusters,
            "potential_bridges": self.potential_bridges,
            "missing_connections": self.missing_connections,
            "exit_analysis": exit_analysis,
            "recommendations": recommendations
        }
        
        self._print_analysis_results(results)
        return results
    
    def _find_reachable_rooms(self, start_room: str) -> None:
        """Find all reachable rooms using BFS."""
        
        queue = deque([start_room])
        
        while queue:
            room_id = queue.popleft()
            
            if room_id in self.reachable_rooms:
                continue
                
            room = self.world.get_room(room_id)
            if not room:
                continue
                
            self.reachable_rooms.add(room_id)
            
            # Add connected rooms
            for target in room.exits.values():
                if target not in self.reachable_rooms and target in self.world.rooms:
                    queue.append(target)
        
        # Identify unreachable rooms
        all_rooms = set(self.world.rooms.keys())
        self.unreachable_rooms = all_rooms - self.reachable_rooms
    
    def _find_unreachable_clusters(self) -> List[Dict]:
        """Group unreachable rooms into connected clusters."""
        
        clusters = []
        unassigned = set(self.unreachable_rooms)
        
        while unassigned:
            # Start new cluster with first unassigned room
            seed_room = next(iter(unassigned))
            cluster_rooms = set()
            queue = deque([seed_room])
            
            # BFS within unreachable rooms only
            while queue:
                room_id = queue.popleft()
                
                if room_id in cluster_rooms:
                    continue
                    
                room = self.world.get_room(room_id)
                if not room or room_id not in unassigned:
                    continue
                    
                cluster_rooms.add(room_id)
                unassigned.remove(room_id)
                
                # Add connected unreachable rooms
                for target in room.exits.values():
                    if target in unassigned and target not in cluster_rooms:
                        queue.append(target)
            
            # Analyze cluster
            cluster_info = self._analyze_cluster(cluster_rooms)
            clusters.append(cluster_info)
        
        return clusters
    
    def _analyze_cluster(self, cluster_rooms: Set[str]) -> Dict:
        """Analyze a cluster of unreachable rooms."""
        
        # Find external connections (exits pointing outside the cluster)
        external_exits = []
        internal_exits = []
        
        for room_id in cluster_rooms:
            room = self.world.get_room(room_id)
            if room:
                for direction, target in room.exits.items():
                    if target in cluster_rooms:
                        internal_exits.append((room_id, direction, target))
                    else:
                        external_exits.append((room_id, direction, target))
        
        # Find entry points (reverse connections from reachable rooms)
        entry_points = []
        for room_id in self.reachable_rooms:
            room = self.world.get_room(room_id)
            if room:
                for direction, target in room.exits.items():
                    if target in cluster_rooms:
                        entry_points.append((room_id, direction, target))
        
        return {
            "size": len(cluster_rooms),
            "rooms": list(cluster_rooms)[:10],  # Show first 10 rooms
            "external_exits": external_exits[:5],  # Show first 5 exits
            "entry_points": entry_points,
            "internal_connectivity": len(internal_exits)
        }
    
    def _find_potential_bridges(self) -> None:
        """Find potential bridge connections between reachable and unreachable areas."""
        
        # Look for rooms that reference each other but aren't connected
        for room_id in self.reachable_rooms:
            room = self.world.get_room(room_id)
            if room:
                for direction, target in room.exits.items():
                    if target in self.unreachable_rooms:
                        self.potential_bridges.append({
                            "type": "reachable_to_unreachable",
                            "from": room_id,
                            "direction": direction,
                            "to": target,
                            "status": "exists" if target in self.world.rooms else "missing_room"
                        })
        
        # Look for reverse connections
        for room_id in self.unreachable_rooms:
            room = self.world.get_room(room_id)
            if room:
                for direction, target in room.exits.items():
                    if target in self.reachable_rooms:
                        self.potential_bridges.append({
                            "type": "unreachable_to_reachable", 
                            "from": room_id,
                            "direction": direction,
                            "to": target,
                            "status": "blocked_connection"
                        })
    
    def _analyze_exit_patterns(self) -> Dict:
        """Analyze exit patterns to identify systemic issues."""
        
        reachable_exit_count = 0
        unreachable_exit_count = 0
        missing_target_count = 0
        
        reachable_directions = defaultdict(int)
        unreachable_directions = defaultdict(int)
        
        for room_id, room in self.world.rooms.items():
            for direction, target in room.exits.items():
                if room_id in self.reachable_rooms:
                    reachable_exit_count += 1
                    reachable_directions[direction] += 1
                else:
                    unreachable_exit_count += 1 
                    unreachable_directions[direction] += 1
                
                if target not in self.world.rooms:
                    missing_target_count += 1
        
        return {
            "reachable_exits": reachable_exit_count,
            "unreachable_exits": unreachable_exit_count,
            "missing_targets": missing_target_count,
            "reachable_direction_distribution": dict(reachable_directions),
            "unreachable_direction_distribution": dict(unreachable_directions)
        }
    
    def _generate_recommendations(self, clusters: List[Dict]) -> List[Dict]:
        """Generate specific recommendations to improve connectivity."""
        
        recommendations = []
        
        # Recommendation 1: Fix missing room references
        if self.missing_connections:
            recommendations.append({
                "priority": "HIGH",
                "type": "fix_missing_rooms",
                "description": f"Fix {len(self.missing_connections)} broken exit references",
                "action": "Create missing rooms or fix exit targets",
                "examples": self.missing_connections[:3]
            })
        
        # Recommendation 2: Connect largest clusters
        if clusters:
            largest_cluster = max(clusters, key=lambda c: c["size"])
            recommendations.append({
                "priority": "HIGH", 
                "type": "connect_largest_cluster",
                "description": f"Connect cluster of {largest_cluster['size']} rooms",
                "action": "Add bidirectional exits between reachable and unreachable areas",
                "cluster_info": largest_cluster
            })
        
        # Recommendation 3: Bridge connections
        if self.potential_bridges:
            bridge_count = len([b for b in self.potential_bridges if b["type"] == "reachable_to_unreachable"])
            recommendations.append({
                "priority": "MEDIUM",
                "type": "enable_bridge_connections", 
                "description": f"Enable {bridge_count} potential bridge connections",
                "action": "Check if exits should be bidirectional or add return paths",
                "examples": self.potential_bridges[:3]
            })
        
        return recommendations
    
    def _print_analysis_results(self, results: Dict) -> None:
        """Print detailed analysis results."""
        
        print(f"\n📊 **CONNECTIVITY ANALYSIS RESULTS**")
        print(f"   Reachable rooms:    {results['reachable_count']}")
        print(f"   Unreachable rooms:  {results['unreachable_count']}")
        print(f"   Connectivity rate:  {results['reachable_count']/(results['reachable_count']+results['unreachable_count'])*100:.1f}%")
        
        # Cluster analysis
        clusters = results['unreachable_clusters']
        print(f"\n🏝️  **UNREACHABLE CLUSTERS** ({len(clusters)} found):")
        
        for i, cluster in enumerate(clusters[:5]):  # Show top 5 clusters
            print(f"   Cluster {i+1}: {cluster['size']} rooms")
            print(f"      Entry points: {len(cluster['entry_points'])}")
            print(f"      External exits: {len(cluster['external_exits'])}")
            if cluster['rooms']:
                print(f"      Sample rooms: {', '.join(cluster['rooms'][:3])}")
        
        if len(clusters) > 5:
            print(f"   ... and {len(clusters) - 5} more clusters")
        
        # Bridge analysis
        bridges = results['potential_bridges']
        print(f"\n🌉 **POTENTIAL BRIDGES** ({len(bridges)} found):")
        
        reachable_to_unreachable = [b for b in bridges if b['type'] == 'reachable_to_unreachable']
        unreachable_to_reachable = [b for b in bridges if b['type'] == 'unreachable_to_reachable']
        
        print(f"   Reachable → Unreachable: {len(reachable_to_unreachable)}")
        print(f"   Unreachable → Reachable: {len(unreachable_to_reachable)}")
        
        # Show examples
        for bridge in bridges[:3]:
            print(f"      {bridge['from']} --{bridge['direction']}--> {bridge['to']} ({bridge['status']})")
        
        # Recommendations
        recommendations = results['recommendations']
        print(f"\n💡 **RECOMMENDATIONS** ({len(recommendations)} items):")
        
        for rec in recommendations:
            print(f"   [{rec['priority']}] {rec['description']}")
            print(f"      Action: {rec['action']}")
    
    def save_gap_analysis(self, filename: str = "connectivity_gap_analysis.json") -> Path:
        """Save gap analysis to file."""
        
        # Run analysis if not done yet
        if not self.reachable_rooms:
            self.analyze_connectivity_gaps()
        
        filepath = Path(__file__).parent / filename
        
        analysis_data = {
            "reachable_rooms": list(self.reachable_rooms),
            "unreachable_rooms": list(self.unreachable_rooms),
            "potential_bridges": self.potential_bridges,
            "missing_connections": self.missing_connections,
            "room_details": {
                room_id: {
                    "reachable": room_id in self.reachable_rooms,
                    "exits": self.world.get_room(room_id).exits if self.world.get_room(room_id) else {}
                }
                for room_id in list(self.reachable_rooms)[:50] + list(self.unreachable_rooms)[:50]  # Sample rooms
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\n📄 Gap analysis saved to: {filepath}")
        return filepath


def main():
    """Run connectivity gap analysis."""
    
    print("🔍 ZORK CONNECTIVITY GAP ANALYZER")
    print("=" * 50)
    
    # Load game world
    print("📚 Loading world...")
    game = GameEngine(use_mud_files=True)
    
    if not game.world.rooms:
        print("❌ No rooms loaded!")
        return False
    
    print(f"✅ Loaded {len(game.world.rooms)} rooms")
    
    # Run gap analysis
    analyzer = ConnectivityGapAnalyzer(game)
    results = analyzer.analyze_connectivity_gaps()
    
    # Save analysis
    analyzer.save_gap_analysis()
    
    # Overall assessment
    connectivity_rate = results['reachable_count'] / (results['reachable_count'] + results['unreachable_count'])
    
    print(f"\n🎯 **GAP ANALYSIS COMPLETE**")
    print(f"   Connectivity: {connectivity_rate:.1%}")
    print(f"   Clusters: {len(results['unreachable_clusters'])}")  
    print(f"   Bridges: {len(results['potential_bridges'])}")
    
    return connectivity_rate > 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)