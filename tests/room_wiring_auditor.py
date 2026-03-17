#!/usr/bin/env python3
"""
Room wiring audit system - Validates all room connections in the Zork world.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
from src.game import GameEngine


@dataclass
class WiringIssue:
    """Represents a room wiring problem."""
    room_id: str
    issue_type: str
    description: str
    direction: Optional[str] = None
    target_room: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical


class RoomWiringAuditor:
    """Comprehensive room wiring validation and connectivity testing."""
    
    def __init__(self, game_engine: GameEngine):
        self.game = game_engine
        self.world = game_engine.world
        self.issues: List[WiringIssue] = []
        
    def audit_all_rooms(self) -> Dict[str, any]:
        """Perform comprehensive audit of all room connections."""
        print("Starting Comprehensive Room Wiring Audit")
        print("=" * 50)
        
        results = {
            "total_rooms": len(self.world.rooms),
            "issues": [],
            "orphaned_rooms": [],
            "unreachable_rooms": [],
            "one_way_connections": [],
            "invalid_exits": [],
            "connectivity_map": {},
            "major_areas": {}
        }
        
        # Clear previous issues
        self.issues.clear()
        
        # 1. Check for invalid exits (pointing to non-existent rooms)
        print("\n1. Checking for invalid exits...")
        invalid_exits = self._check_invalid_exits()
        results["invalid_exits"] = invalid_exits
        
        # 2. Check for orphaned rooms (no incoming connections)
        print(f"   Found {len(invalid_exits)} invalid exits")
        print("\n2. Checking for orphaned rooms...")
        orphaned_rooms = self._find_orphaned_rooms()
        results["orphaned_rooms"] = orphaned_rooms
        print(f"   Found {len(orphaned_rooms)} orphaned rooms")
        
        # 3. Check connectivity from starting room
        print("\n3. Testing world connectivity...")
        reachable_rooms = self._test_connectivity_from_start()
        unreachable = set(self.world.rooms.keys()) - reachable_rooms
        results["unreachable_rooms"] = list(unreachable)
        print(f"   {len(reachable_rooms)} rooms reachable from start")
        print(f"   {len(unreachable)} rooms unreachable from start")
        
        # 4. Identify one-way connections that might need to be bidirectional
        print("\n4. Checking for one-way connections...")
        one_way_connections = self._find_one_way_connections()
        results["one_way_connections"] = one_way_connections
        print(f"   Found {len(one_way_connections)} one-way connections")
        
        # 5. Map major game areas and their connectivity
        print("\n5. Mapping major game areas...")
        area_map = self._map_major_areas()
        results["major_areas"] = area_map
        
        # 6. Generate connectivity statistics
        print("\n6. Generating connectivity statistics...")
        connectivity_stats = self._generate_connectivity_stats()
        results["connectivity_map"] = connectivity_stats
        
        # Compile all issues
        results["issues"] = [
            {
                "room_id": issue.room_id,
                "type": issue.issue_type,
                "description": issue.description,
                "direction": issue.direction,
                "target": issue.target_room,
                "severity": issue.severity
            }
            for issue in self.issues
        ]
        
        return results
    
    def _check_invalid_exits(self) -> List[Dict[str, str]]:
        """Check for exits that point to non-existent rooms."""
        invalid_exits = []
        
        for room_id, room in self.world.rooms.items():
            for direction, target_id in room.exits.items():
                if target_id not in self.world.rooms:
                    invalid_exit = {
                        "room_id": room_id,
                        "room_name": room.name,
                        "direction": direction,
                        "target_id": target_id,
                        "description": room.description[:50] + "..." if len(room.description) > 50 else room.description
                    }
                    invalid_exits.append(invalid_exit)
                    
                    self.issues.append(WiringIssue(
                        room_id=room_id,
                        issue_type="invalid_exit",
                        description=f"Exit {direction} points to non-existent room {target_id}",
                        direction=direction,
                        target_room=target_id,
                        severity="high"
                    ))
        
        return invalid_exits
    
    def _find_orphaned_rooms(self) -> List[Dict[str, str]]:
        """Find rooms that have no incoming connections."""
        incoming_connections = set()
        
        # Collect all rooms that are targets of exits
        for room_id, room in self.world.rooms.items():
            for direction, target_id in room.exits.items():
                if target_id in self.world.rooms:  # Only count valid targets
                    incoming_connections.add(target_id)
        
        # Starting room is not orphaned by definition
        incoming_connections.add("WHOUS")
        
        orphaned_rooms = []
        for room_id, room in self.world.rooms.items():
            if room_id not in incoming_connections:
                orphaned_rooms.append({
                    "room_id": room_id,
                    "room_name": room.name,
                    "description": room.description[:50] + "..." if len(room.description) > 50 else room.description,
                    "exits": list(room.exits.keys())
                })
                
                self.issues.append(WiringIssue(
                    room_id=room_id,
                    issue_type="orphaned_room",
                    description=f"Room has no incoming connections (orphaned)",
                    severity="medium"
                ))
        
        return orphaned_rooms
    
    def _test_connectivity_from_start(self) -> Set[str]:
        """Test which rooms are reachable from the starting room using BFS."""
        start_room = "WHOUS"
        visited = set()
        queue = deque([start_room])
        visited.add(start_room)
        
        while queue:
            current_room_id = queue.popleft()
            current_room = self.world.rooms.get(current_room_id)
            
            if not current_room:
                continue
                
            for direction, target_id in current_room.exits.items():
                if target_id in self.world.rooms and target_id not in visited:
                    visited.add(target_id)
                    queue.append(target_id)
        
        return visited
    
    def _find_one_way_connections(self) -> List[Dict[str, str]]:
        """Find connections that only go one way."""
        one_way_connections = []
        
        # Mapping of reverse directions
        reverse_dirs = {
            "north": "south", "south": "north",
            "east": "west", "west": "east",
            "northeast": "southwest", "southwest": "northeast",
            "northwest": "southeast", "southeast": "northwest",
            "up": "down", "down": "up"
        }
        
        for room_id, room in self.world.rooms.items():
            for direction, target_id in room.exits.items():
                if target_id not in self.world.rooms:
                    continue  # Skip invalid exits (already reported)
                
                # Check if there's a reverse connection
                target_room = self.world.rooms[target_id]
                reverse_direction = reverse_dirs.get(direction)
                
                if reverse_direction:
                    reverse_target = target_room.exits.get(reverse_direction)
                    if reverse_target != room_id:
                        one_way_connections.append({
                            "from_room": room_id,
                            "from_name": room.name,
                            "to_room": target_id,
                            "to_name": target_room.name,
                            "direction": direction,
                            "reverse_direction": reverse_direction,
                            "has_reverse": reverse_target is not None,
                            "reverse_target": reverse_target
                        })
                        
                        # Only add as issue if it's a standard direction that should be bidirectional
                        if direction in reverse_dirs:
                            self.issues.append(WiringIssue(
                                room_id=room_id,
                                issue_type="one_way_connection",
                                description=f"One-way connection {direction} to {target_id} (no reverse {reverse_direction})",
                                direction=direction,
                                target_room=target_id,
                                severity="low"
                            ))
        
        return one_way_connections
    
    def _map_major_areas(self) -> Dict[str, List[str]]:
        """Identify and map major game areas."""
        
        # Define known major areas based on room naming patterns
        area_patterns = {
            "House Area": ["WHOUS", "NHOUS", "SHOUS", "EHOUS", "KITCH", "ATTIC", "LROOM"],
            "Forest Area": ["FORE1", "FORE2", "FORE3", "FORE4", "FORE5", "TREE", "CLEAR"],
            "Cellar/Underground": ["CELLA", "MTROL", "STUDI", "GALLE"],
            "Maze Complex": [f"MAZE{i}" for i in range(1, 16)] + [f"MAZ{i:02d}" for i in range(10, 16)] + [f"DEAD{i}" for i in range(1, 8)],
            "Cyclops/Treasure Area": ["CYCLO", "BLROO", "TREAS", "MGRAT"],
            "River/Water Area": [f"RIVR{i}" for i in range(1, 6)] + ["DAM", "LOBBY", "MAINT", "DOCK", "FALLS", "RAINB"],
            "Cliff/Mountain Area": ["CLBOT", "CLMID", "CLTOP", "LEDG2", "LEDG3", "LEDG4"],
            "Mirror Room Complex": ["MIRR1", "MIRR2", "INMIR", "MRANT", "MREYE"],
            "Temple/Egypt Area": ["EGYPT", "TEMP1", "TEMP2"],
            "Atlantis Area": ["ATLAN"],
            "Volcano/Lava Area": ["VLBOT", "VAIR1", "VAIR2", "VAIR3", "VAIR4", "LAVA", "MAGNE"],
            "Machine/Tech Area": ["MACHI", "CMACH"],
            "Tomb/Crypt Area": ["TOMB", "CRYPT", "TSTRS"],
            "Corridor Complex": ["ECORR", "WCORR", "SCORR", "NCORR", "BDOOR", "FDOOR"],
            "Prison/Cell Area": ["PARAP", "CELL", "PCELL", "NCELL"],
            "Book/Library Area": ["BKENT", "BKTW", "BKTE", "BKVW", "BKVE", "BKTWI", "BKVAU", "BKBOX", "BKEXE", "ALICE", "ALISM", "ALITR", "LIBRA"],
            "Carousel Area": ["CAROU", "PASS1", "PASS5"],
            "Slide Area": ["SLIDE", "SLID1", "SLID2", "SLID3", "SLEDG", "SPAL"],
            "Coal Mine": ["MINE1", "MINE2", "MINE3", "MINE4", "MINE5", "MINE6", "MINE7", "DOME", "MTORC"],
            "Shaft Areas": ["TSHAF", "BSHAF"]
        }
        
        # Find rooms in each area and check their connectivity
        area_map = {}
        for area_name, room_list in area_patterns.items():
            existing_rooms = [room_id for room_id in room_list if room_id in self.world.rooms]
            if existing_rooms:
                area_map[area_name] = existing_rooms
        
        return area_map
    
    def _generate_connectivity_stats(self) -> Dict[str, any]:
        """Generate detailed connectivity statistics."""
        stats = {
            "total_rooms": len(self.world.rooms),
            "total_exits": 0,
            "rooms_by_exit_count": defaultdict(int),
            "most_connected_rooms": [],
            "least_connected_rooms": [],
            "average_connections": 0
        }
        
        room_connections = []
        
        for room_id, room in self.world.rooms.items():
            exit_count = len(room.exits)
            stats["total_exits"] += exit_count
            stats["rooms_by_exit_count"][exit_count] += 1
            
            room_connections.append({
                "room_id": room_id,
                "room_name": room.name,
                "exit_count": exit_count,
                "exits": dict(room.exits)
            })
        
        # Sort by connection count
        room_connections.sort(key=lambda x: x["exit_count"], reverse=True)
        
        stats["most_connected_rooms"] = room_connections[:10]
        stats["least_connected_rooms"] = room_connections[-10:]
        stats["average_connections"] = stats["total_exits"] / len(self.world.rooms) if self.world.rooms else 0
        
        return stats
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """Generate a comprehensive text report of the audit results."""
        report = []
        report.append("ZORK WORLD WIRING AUDIT REPORT")
        report.append("=" * 50)
        report.append(f"Total Rooms Analyzed: {results['total_rooms']}")
        report.append(f"Total Issues Found: {len(results['issues'])}")
        report.append("")
        
        # Critical Issues
        critical_issues = [i for i in results['issues'] if i['severity'] == 'critical']
        high_issues = [i for i in results['issues'] if i['severity'] == 'high']
        
        if critical_issues:
            report.append("🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                report.append(f"  ❌ {issue['room_id']}: {issue['description']}")
            report.append("")
        
        if high_issues:
            report.append("⚠️  HIGH PRIORITY ISSUES:")
            for issue in high_issues:
                report.append(f"  🔴 {issue['room_id']}: {issue['description']}")
            report.append("")
        
        # Invalid Exits
        if results['invalid_exits']:
            report.append(f"🔌 INVALID EXITS ({len(results['invalid_exits'])}):")
            for invalid in results['invalid_exits'][:10]:  # Show first 10
                report.append(f"  ❌ {invalid['room_id']} -> {invalid['direction']} -> {invalid['target_id']} (NOT FOUND)")
            if len(results['invalid_exits']) > 10:
                report.append(f"  ... and {len(results['invalid_exits']) - 10} more")
            report.append("")
        
        # Connectivity Summary  
        report.append("🌐 CONNECTIVITY SUMMARY:")
        report.append(f"  ✅ Reachable from start: {results['total_rooms'] - len(results['unreachable_rooms'])} rooms")
        if results['unreachable_rooms']:
            report.append(f"  ❌ Unreachable rooms: {len(results['unreachable_rooms'])}")
            for room in results['unreachable_rooms'][:5]:
                report.append(f"    - {room}")
            if len(results['unreachable_rooms']) > 5:
                report.append(f"    ... and {len(results['unreachable_rooms']) - 5} more")
        report.append("")
        
        # Major Areas
        report.append("🏛️  MAJOR AREAS:")
        for area_name, rooms in results['major_areas'].items():
            report.append(f"  📍 {area_name}: {len(rooms)} rooms")
        report.append("")
        
        # Connection Statistics
        conn_stats = results['connectivity_map']
        report.append("📊 CONNECTION STATISTICS:")
        report.append(f"  Average connections per room: {conn_stats['average_connections']:.1f}")
        report.append(f"  Most connected room: {conn_stats['most_connected_rooms'][0]['room_id']} ({conn_stats['most_connected_rooms'][0]['exit_count']} exits)")
        report.append(f"  Least connected rooms: {len([r for r in conn_stats['least_connected_rooms'] if r['exit_count'] <= 1])} rooms with ≤1 exit")
        
        return "\n".join(report)


def main():
    """Run the room wiring audit."""
    print("Initializing Zork world for wiring audit...")
    game = GameEngine(use_mud_files=True)
    
    print(f"Loaded {len(game.world.rooms)} rooms from Zork source files")
    
    auditor = RoomWiringAuditor(game)
    results = auditor.audit_all_rooms()
    
    # Generate and display report
    report = auditor.generate_report(results)
    print("\n" + report)
    
    # Save detailed results to file
    import json
    with open("room_wiring_audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Detailed results saved to: room_wiring_audit_results.json")
    
    # Summary
    total_issues = len(results['issues'])
    critical_count = len([i for i in results['issues'] if i['severity'] == 'critical'])
    high_count = len([i for i in results['issues'] if i['severity'] == 'high'])
    
    print(f"\n📋 AUDIT SUMMARY:")
    print(f"   Total Issues: {total_issues}")
    print(f"   Critical: {critical_count}")
    print(f"   High Priority: {high_count}")
    print(f"   Invalid Exits: {len(results['invalid_exits'])}")
    print(f"   Unreachable Rooms: {len(results['unreachable_rooms'])}")
    
    if total_issues == 0:
        print("   ✅ No major wiring issues detected!")
    elif critical_count > 0:
        print("   🚨 Critical issues require immediate attention!")
    elif high_count > 0:
        print("   ⚠️  High priority issues should be addressed soon.")
    else:
        print("   ℹ️  Only minor issues detected.")


if __name__ == "__main__":
    main()