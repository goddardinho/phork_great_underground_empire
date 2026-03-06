#!/usr/bin/env python3
"""
Comprehensive Zork World Validator
Validates starting location, room descriptions, contents, and exits against canonical Zork
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game import GameEngine
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
import json
from pathlib import Path

@dataclass
class ValidationIssue:
    category: str
    severity: str  # "critical", "high", "medium", "low"
    room_id: str
    issue: str
    expected: str
    actual: str
    
class ZorkWorldValidator:
    def __init__(self):
        self.issues: List[ValidationIssue] = []
        self.game_engine = None
    
    def validate_all(self) -> Dict:
        """Run comprehensive validation of the entire Zork world."""
        print("🔍 Starting Comprehensive Zork World Validation")
        print("=" * 60)
        
        # Initialize game engine
        print("Initializing game engine...")
        self.game_engine = GameEngine(use_mud_files=True)
        
        # Run all validation checks
        results = {}
        results['starting_location'] = self._validate_starting_location()
        results['room_descriptions'] = self._validate_room_descriptions()
        results['room_contents'] = self._validate_room_contents()
        results['room_exits'] = self._validate_room_exits()
        results['canonical_gameplay'] = self._validate_canonical_gameplay()
        results['world_integrity'] = self._validate_world_integrity()
        
        # Generate summary
        results['summary'] = self._generate_summary()
        
        return results
    
    def _validate_starting_location(self) -> Dict:
        """Validate the canonical starting location."""
        print("\n1. Validating starting location...")
        
        expected_start = "WHOUS"  # West of House
        actual_start = self.game_engine.player.current_room
        
        if actual_start != expected_start:
            self.issues.append(ValidationIssue(
                category="starting_location",
                severity="critical", 
                room_id=actual_start,
                issue="Incorrect starting location",
                expected=expected_start,
                actual=actual_start
            ))
            
        # Validate starting room properties
        start_room = self.game_engine.world.get_room(expected_start)
        if start_room:
            # Check description
            if "west of" not in start_room.description.lower():
                self.issues.append(ValidationIssue(
                    category="starting_location",
                    severity="high",
                    room_id=expected_start,
                    issue="Starting room description doesn't mention 'west of'",
                    expected="Description containing 'west of'",
                    actual=start_room.description
                ))
                
            # Check basic exits
            expected_exits = {"north", "south", "east"}  # Should lead to other sides of house
            actual_exits = set(start_room.exits.keys())
            missing_exits = expected_exits - actual_exits
            
            if missing_exits:
                self.issues.append(ValidationIssue(
                    category="starting_location", 
                    severity="high",
                    room_id=expected_start,
                    issue=f"Missing expected exits: {missing_exits}",
                    expected=str(expected_exits),
                    actual=str(actual_exits)
                ))
        
        return {
            "expected_start": expected_start,
            "actual_start": actual_start,
            "valid": actual_start == expected_start,
            "issues_found": len([i for i in self.issues if i.category == "starting_location"])
        }
    
    def _validate_room_descriptions(self) -> Dict:
        """Validate room descriptions against known canonical descriptions.""" 
        print("2. Validating room descriptions...")
        
        # Known canonical descriptions for key rooms
        canonical_descriptions = {
            "WHOUS": ["west of", "white house", "closed", "boarded up"],
            "NHOUS": ["north of", "white house"],  
            "SHOUS": ["south of", "white house"],
            "EHOUS": ["behind", "white house", "window"],  # Behind house has window
            "LROOM": ["living room", "door", "east"],
            "KITCH": ["kitchen", "table", "food", "window", "passage", "west", "staircase", "upward"], 
            "ATTIC": ["attic", "dusty"],
            "CELLA": ["cellar", "stone walls"],
            "FORE1": ["forest", "path"],
            "FORE2": ["forest"],
            "FORE3": ["forest"],
            "CLEAR": ["clearing", "leaves"],
            "MGRAT": ["grating", "steel grating"],
            "MAZE1": ["maze", "twisty", "passages"],
        }
        
        description_issues = 0
        
        for room_id, expected_keywords in canonical_descriptions.items():
            room = self.game_engine.world.get_room(room_id)
            if not room:
                self.issues.append(ValidationIssue(
                    category="room_descriptions",
                    severity="critical",
                    room_id=room_id,
                    issue="Room not found in world",
                    expected="Room should exist",
                    actual="Room missing"
                ))
                description_issues += 1
                continue
                
            description = room.description.lower()
            
            # Check for expected keywords
            missing_keywords = []
            for keyword in expected_keywords:
                if keyword.lower() not in description:
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                self.issues.append(ValidationIssue(
                    category="room_descriptions",
                    severity="medium",
                    room_id=room_id, 
                    issue=f"Missing expected keywords: {missing_keywords}",
                    expected=f"Description containing: {expected_keywords}",
                    actual=description[:100] + "..." if len(description) > 100 else description
                ))
                description_issues += 1
        
        # Check for empty descriptions
        empty_descriptions = 0
        for room_id, room in self.game_engine.world.rooms.items():
            if not room.description.strip():
                self.issues.append(ValidationIssue(
                    category="room_descriptions",
                    severity="high", 
                    room_id=room_id,
                    issue="Empty room description",
                    expected="Non-empty description",
                    actual="Empty string"
                ))
                empty_descriptions += 1
        
        return {
            "total_rooms": len(self.game_engine.world.rooms),
            "canonical_checks": len(canonical_descriptions),
            "description_issues": description_issues,
            "empty_descriptions": empty_descriptions
        }
    
    def _validate_room_contents(self) -> Dict:
        """Validate objects are in correct rooms."""
        print("3. Validating room contents...")
        
        # Known canonical object placements
        canonical_contents = {
            "WHOUS": ["MAILX"],  # Mailbox at west of house
            "LROOM": ["LAMP", "RUG", "TCASE", "SWORD", "DOOR"],  # Living room items
            "KITCH": ["BOTTL", "SBAG"],  # Kitchen items
            "ATTIC": ["ROPE", "KNIFE"],  # Attic items 
            "MGRAT": ["GRATE", "KEYS"],  # Grating room
            "CELLA": [],  # Cellar starts empty
        }
        
        content_issues = 0
        
        for room_id, expected_objects in canonical_contents.items():
            room = self.game_engine.world.get_room(room_id)
            if not room:
                continue
                
            # Get actual objects in room
            actual_objects = room.items
            
            # Check for missing expected objects
            for expected_obj in expected_objects:
                if expected_obj not in actual_objects:
                    self.issues.append(ValidationIssue(
                        category="room_contents",
                        severity="high",
                        room_id=room_id,
                        issue=f"Missing expected object: {expected_obj}",
                        expected=str(expected_objects),
                        actual=str(actual_objects)
                    ))
                    content_issues += 1
        
        # Check for critical starting objects
        critical_objects = ["LAMP", "SWORD", "MAILX", "GRATE"]
        for obj_id in critical_objects:
            found = False
            for room in self.game_engine.world.rooms.values():
                if obj_id in room.items:
                    found = True
                    break
            
            # Also check if object exists in game engine's object registry
            if not found and obj_id in self.game_engine.objects:
                found = True
            
            if not found:
                self.issues.append(ValidationIssue(
                    category="room_contents",
                    severity="critical", 
                    room_id="GLOBAL",
                    issue=f"Critical object {obj_id} not found anywhere in world",
                    expected=f"Object {obj_id} should exist",
                    actual="Object missing"
                ))
                content_issues += 1
        
        return {
            "canonical_rooms_checked": len(canonical_contents),
            "content_issues": content_issues,
            "critical_objects": critical_objects
        }
    
    def _validate_room_exits(self) -> Dict:
        """Validate room exits match canonical Zork."""
        print("4. Validating room exits...")
        
        # Key canonical exit patterns
        canonical_exits = {
            "WHOUS": {"north": "NHOUS", "south": "SHOUS", "east": "EHOUS"},
            "NHOUS": {"south": "WHOUS", "east": "EHOUS"},
            "SHOUS": {"north": "WHOUS", "east": "EHOUS"},
            "EHOUS": {"west": "WHOUS", "north": "NHOUS", "south": "SHOUS"},
            "LROOM": {"east": "KITCH", "down": "CELLA"},  # Critical trapdoor connection
            "KITCH": {"west": "LROOM", "up": "ATTIC"},
            "CELLA": {"up": "LROOM", "east": "MTROL"},  # Critical underground entrance
        }
        
        exit_issues = 0
        
        for room_id, expected_exits in canonical_exits.items():
            room = self.game_engine.world.get_room(room_id)
            if not room:
                continue
                
            actual_exits = room.exits
            
            # Check each expected exit
            for direction, expected_target in expected_exits.items():
                if direction not in actual_exits:
                    self.issues.append(ValidationIssue(
                        category="room_exits",
                        severity="high",
                        room_id=room_id,
                        issue=f"Missing exit: {direction} -> {expected_target}",
                        expected=f"{direction}: {expected_target}",
                        actual=f"No {direction} exit"
                    ))
                    exit_issues += 1
                elif actual_exits[direction] != expected_target:
                    self.issues.append(ValidationIssue(
                        category="room_exits", 
                        severity="high",
                        room_id=room_id,
                        issue=f"Wrong exit target: {direction}",
                        expected=f"{direction}: {expected_target}",
                        actual=f"{direction}: {actual_exits[direction]}"
                    ))
                    exit_issues += 1
        
        # Validate bidirectional connections
        bidirectional_issues = 0
        for room_id, room in self.game_engine.world.rooms.items():
            for direction, target_id in room.exits.items():
                target_room = self.game_engine.world.get_room(target_id)
                if not target_room:
                    continue
                    
                # Check if return path exists (not all connections are bidirectional)
                opposite_direction = {
                    "north": "south", "south": "north",
                    "east": "west", "west": "east", 
                    "up": "down", "down": "up"
                }.get(direction)
                
                if opposite_direction and opposite_direction in target_room.exits:
                    if target_room.exits[opposite_direction] != room_id:
                        # This might be intentional (one-way passages) so mark as medium severity
                        self.issues.append(ValidationIssue(
                            category="room_exits",
                            severity="low",
                            room_id=room_id,
                            issue=f"One-way connection: {direction} to {target_id}",
                            expected=f"Bidirectional connection", 
                            actual=f"One-way: {room_id}->{target_id} but {target_id} doesn't lead back"
                        ))
                        bidirectional_issues += 1
        
        return {
            "canonical_rooms_checked": len(canonical_exits),
            "exit_issues": exit_issues,
            "bidirectional_issues": bidirectional_issues
        }
    
    def _validate_canonical_gameplay(self) -> Dict:
        """Test canonical Zork gameplay sequences."""
        print("5. Validating canonical gameplay...")
        
        gameplay_issues = 0
        
        # Test 1: Can move around house
        try:
            original_room = self.game_engine.player.current_room
            
            # Try moving around the house perimeter
            moves = ["north", "east", "south", "west"]
            for move in moves:
                if not self.game_engine.handle_command(move):
                    self.issues.append(ValidationIssue(
                        category="canonical_gameplay",
                        severity="high",
                        room_id=self.game_engine.player.current_room,
                        issue=f"Cannot move {move} from room",
                        expected=f"Movement {move} should work",
                        actual="Movement failed"
                    ))
                    gameplay_issues += 1
            
            # Return to starting position
            self.game_engine.player.move_to_room(self.game_engine.world.get_room(original_room))
        except Exception as e:
            self.issues.append(ValidationIssue(
                category="canonical_gameplay",
                severity="critical",
                room_id=self.game_engine.player.current_room,
                issue=f"Exception during movement test: {str(e)}",
                expected="Successful movement",
                actual=f"Exception: {str(e)}"
            ))
            gameplay_issues += 1
        
        # Test 2: Can access underground
        try:
            # Go to living room  
            self.game_engine.player.move_to_room(self.game_engine.world.get_room("LROOM"))
            
            # Try going down (trapdoor should work)
            if not self.game_engine.handle_command("down"):
                self.issues.append(ValidationIssue(
                    category="canonical_gameplay",
                    severity="critical",
                    room_id="LROOM",
                    issue="Cannot go down from living room to cellar",
                    expected="Down exit should lead to cellar",
                    actual="Down movement failed"
                ))
                gameplay_issues += 1
            elif self.game_engine.player.current_room != "CELLA":
                self.issues.append(ValidationIssue(
                    category="canonical_gameplay", 
                    severity="critical",
                    room_id="LROOM",
                    issue="Down from living room leads to wrong room",
                    expected="Should lead to CELLA",
                    actual=f"Leads to {self.game_engine.player.current_room}"
                ))  
                gameplay_issues += 1
                
            # Return to start
            self.game_engine.player.move_to_room(self.game_engine.world.get_room("WHOUS"))
        except Exception as e:
            self.issues.append(ValidationIssue(
                category="canonical_gameplay",
                severity="critical", 
                room_id=self.game_engine.player.current_room,
                issue=f"Exception during underground test: {str(e)}",
                expected="Successful underground access",
                actual=f"Exception: {str(e)}"
            ))
            gameplay_issues += 1
        
        return {
            "gameplay_issues": gameplay_issues,
            "tests_run": ["house_perimeter", "underground_access"]
        }
    
    def _validate_world_integrity(self) -> Dict:
        """Validate overall world integrity."""
        print("6. Validating world integrity...")
        
        integrity_issues = 0
        
        # Check for duplicate room IDs (shouldn't happen but good to verify)
        room_ids = list(self.game_engine.world.rooms.keys())
        if len(room_ids) != len(set(room_ids)):
            self.issues.append(ValidationIssue(
                category="world_integrity",
                severity="critical",
                room_id="GLOBAL", 
                issue="Duplicate room IDs found",
                expected="All room IDs should be unique",
                actual=f"Found {len(room_ids)} rooms with {len(set(room_ids))} unique IDs"
            ))
            integrity_issues += 1
        
        # Check for rooms with no exits (dead ends should be rare)
        dead_ends = []
        for room_id, room in self.game_engine.world.rooms.items():
            if not room.exits:
                dead_ends.append(room_id)
        
        if len(dead_ends) > 5:  # Allow some dead ends but not too many
            self.issues.append(ValidationIssue(
                category="world_integrity",
                severity="medium",
                room_id="GLOBAL",
                issue=f"Many rooms with no exits: {len(dead_ends)}",
                expected="Most rooms should have exits",
                actual=f"Dead end rooms: {dead_ends[:10]}"  # Show first 10
            ))
            integrity_issues += 1
        
        # Check total room count (original Zork has ~110 rooms, we loaded 196)
        total_rooms = len(self.game_engine.world.rooms)
        if total_rooms < 100:
            self.issues.append(ValidationIssue(
                category="world_integrity", 
                severity="high",
                room_id="GLOBAL",
                issue="Too few rooms loaded",
                expected="Should have 100+ rooms",
                actual=f"Only {total_rooms} rooms"
            ))
            integrity_issues += 1
        
        return {
            "total_rooms": total_rooms,
            "dead_ends": len(dead_ends),
            "integrity_issues": integrity_issues
        }
    
    def _generate_summary(self) -> Dict:
        """Generate validation summary."""
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        high_issues = [i for i in self.issues if i.severity == "high"] 
        medium_issues = [i for i in self.issues if i.severity == "medium"]
        low_issues = [i for i in self.issues if i.severity == "low"]
        
        return {
            "total_issues": len(self.issues),
            "critical": len(critical_issues),
            "high": len(high_issues),
            "medium": len(medium_issues), 
            "low": len(low_issues),
            "overall_status": "PASS" if len(critical_issues) == 0 else "FAIL"
        }
    
    def save_detailed_report(self, filename: str = "zork_validation_report.json"):
        """Save detailed validation report to JSON file."""
        report_data = {
            "validation_timestamp": "2026-03-06",
            "total_issues": len(self.issues),
            "issues": [
                {
                    "category": issue.category,
                    "severity": issue.severity,
                    "room_id": issue.room_id,
                    "issue": issue.issue,
                    "expected": issue.expected,
                    "actual": issue.actual
                }
                for issue in self.issues
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"📋 Detailed report saved to: {filename}")

def main():
    validator = ZorkWorldValidator()
    results = validator.validate_all()
    
    print("\n" + "=" * 60)
    print("🏆 ZORK WORLD VALIDATION SUMMARY")
    print("=" * 60)
    
    summary = results['summary']
    print(f"Overall Status: {'🟢 PASS' if summary['overall_status'] == 'PASS' else '🔴 FAIL'}")
    print(f"Total Issues: {summary['total_issues']}")
    print(f"  🚨 Critical: {summary['critical']}")
    print(f"  ❗ High: {summary['high']}")
    print(f"  ⚠️  Medium: {summary['medium']}")
    print(f"  ℹ️  Low: {summary['low']}")
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"  Starting Location: {'✅' if results['starting_location']['valid'] else '❌'}")
    print(f"  Room Descriptions: {results['room_descriptions']['total_rooms']} rooms checked")
    print(f"  Room Contents: {results['room_contents']['canonical_rooms_checked']} rooms validated")
    print(f"  Room Exits: {results['room_exits']['canonical_rooms_checked']} rooms validated")
    print(f"  Gameplay Tests: {len(results['canonical_gameplay']['tests_run'])} tests run")
    print(f"  World Integrity: {results['world_integrity']['total_rooms']} rooms analyzed")
    
    # Show critical issues if any
    if summary['critical'] > 0:
        print(f"\n🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:")
        for issue in validator.issues:
            if issue.severity == "critical":
                print(f"   • {issue.room_id}: {issue.issue}")
    
    # Save detailed report
    validator.save_detailed_report()
    
    return results

if __name__ == "__main__":
    main()