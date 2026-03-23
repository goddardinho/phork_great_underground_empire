"""Thief NPC Implementation - Phase 2 of Canonical NPCs Feature

The Thief is the first canonical NPC from original Zork, featuring:
- Object theft mechanics (steals treasures from player)
- Combat integration with enhanced combat stats  
- Movement behavior (roams between rooms)
- Loot dropping when defeated
- Authentic Zork Thief interactions and responses

This implementation provides the foundation for all other canonical NPCs.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import random
import time

from .npc import NPC, DialogueNode, DialogueResponse
from .combat import CombatStats


class ThiefBehavior:
    """Manages Thief-specific behaviors and mechanics."""
    
    def __init__(self, thief_npc: NPC):
        self.thief = thief_npc
        self.stolen_objects: List[str] = []  # Objects stolen from player
        self.last_theft_time = 0
        self.theft_cooldown = 30  # Seconds between theft attempts
        self.movement_timer = 0
        self.movement_interval = 45  # Seconds between room movements
        
        # Thief preferences for what to steal (treasures preferred)
        self.theft_preferences = {
            "treasure": 10,  # High priority for treasure items
            "valuable": 7,   # Medium-high for valuable items  
            "weapon": 5,     # Medium for potential weapons
            "tool": 3,       # Low-medium for tools
            "other": 1       # Low priority for other items
        }
    
    def can_attempt_theft(self) -> bool:
        """Check if Thief can attempt to steal something."""
        current_time = time.time()
        return (current_time - self.last_theft_time) > self.theft_cooldown
    
    def can_move(self) -> bool:
        """Check if Thief can move to a different room."""
        current_time = time.time()  
        return (current_time - self.movement_timer) > self.movement_interval
    
    def get_theft_targets(self, player_inventory: List[str], object_manager) -> List[str]:
        """Get list of objects Thief wants to steal, ordered by preference."""
        targets = []
        
        for item_id in player_inventory:
            obj = object_manager.get_object(item_id)
            if not obj:
                continue
                
            # Calculate theft priority
            priority = 0
            
            # Check for treasure value
            if obj.get_attribute("treasure_value", 0) > 0:
                priority += self.theft_preferences["treasure"]
                
            # Check for valuable items
            if obj.get_attribute("valuable", False):
                priority += self.theft_preferences["valuable"]
                
            # Check for weapons
            if obj.get_attribute("weapon", False) or "sword" in obj.name.lower():
                priority += self.theft_preferences["weapon"]
                
            # Check for tools
            if obj.get_attribute("tool", False) or any(tool in obj.name.lower() for tool in ["key", "lamp", "lantern"]):
                priority += self.theft_preferences["tool"]
            else:
                priority += self.theft_preferences["other"]
            
            targets.append((item_id, priority))
        
        # Sort by priority (highest first) and return item IDs
        targets.sort(key=lambda x: x[1], reverse=True)
        return [item_id for item_id, _ in targets]
    
    def attempt_theft(self, player_inventory: List[str], object_manager) -> Optional[str]:
        """Attempt to steal an object. Returns stolen object ID or None."""
        if not self.can_attempt_theft() or not player_inventory:
            return None
            
        targets = self.get_theft_targets(player_inventory, object_manager)
        if not targets:
            return None
        
        # Thief has 60% chance to successfully steal the preferred item
        if random.random() < 0.6:
            stolen_item = targets[0]  # Take highest priority item
            self.stolen_objects.append(stolen_item)
            self.last_theft_time = time.time()
            return stolen_item
            
        return None
    
    def drop_loot_on_death(self) -> List[str]:
        """Return all stolen objects when Thief is defeated."""
        loot = self.stolen_objects.copy()
        self.stolen_objects.clear()
        return loot
    
    def get_movement_destinations(self, current_room, world) -> List[str]:
        """Get list of rooms Thief can move to."""
        room = world.get_room(current_room)
        if not room or not room.exits:
            return []
        
        # Thief prefers rooms with treasures or player presence
        destinations = list(room.exits.values())
        
        # Filter out dangerous rooms Thief would avoid
        safe_destinations = []
        for room_id in destinations:
            dest_room = world.get_room(room_id) 
            if dest_room and not dest_room.has_flag("deadly"):
                safe_destinations.append(room_id)
        
        return safe_destinations if safe_destinations else destinations
    
    def should_flee_combat(self, thief_health: int, max_health: int) -> bool:
        """Determine if Thief should attempt to flee from combat."""
        health_ratio = thief_health / max_health
        
        # Flee if health is below 30%, or 20% chance if below 60%
        if health_ratio < 0.3:
            return True
        elif health_ratio < 0.6:
            return random.random() < 0.2
            
        return False


def create_canonical_thief(npc_manager, starting_room: str = "WHOUS") -> NPC:
    """Create the canonical Thief NPC with authentic Zork behaviors."""
    
    # Create dialogue nodes for Thief interactions
    encounter_node = DialogueNode(
        id="encounter",
        text="A suspicious thief eyes your belongings hungrily. \"Give me your treasures, and I might let you pass unharmed.\"",
        responses=[
            DialogueResponse(
                id="resp_refuse",
                text="Never! Fight me!",
                next_node="combat_taunt"
            ),
            DialogueResponse(
                id="resp_negotiate", 
                text="Perhaps we can make a deal",
                next_node="negotiation"
            ),
            DialogueResponse(
                id="resp_flee",
                text="I don't want trouble",
                next_node="dismissal"
            )
        ]
    )
    
    combat_taunt_node = DialogueNode(
        id="combat_taunt",
        text="\"So be it! Prepare to meet your doom!\" The thief draws a wicked-looking knife.",
        end_conversation=True
    )
    
    negotiation_node = DialogueNode(
        id="negotiation",
        text="\"Hmm... drop your most valuable item and I'll consider sparing you. But next time, I might not be so generous.\"",
        end_conversation=True
    )
    
    dismissal_node = DialogueNode(
        id="dismissal", 
        text="\"Wise choice. Run along now, but remember - I'll be watching.\" The thief melts back into the shadows.",
        end_conversation=True
    )
    
    # Create Thief with enhanced combat stats
    thief_combat_stats = CombatStats(
        max_health=100,
        current_health=100,
        attack_power=18,  # Higher than default NPCs
        defense=8,
        accuracy=85,      # More skilled than average
        dodge_chance=25,  # Very agile
        block_chance=15,
        critical_chance=12  # Skilled fighter
    )
    
    thief = NPC(
        id="THIEF",
        name="thief",
        description="A ruthless thief lurks here, fingering a wicked-looking knife.",
        location=starting_room,
        dialogue_tree={
            "encounter": encounter_node,
            "combat_taunt": combat_taunt_node, 
            "negotiation": negotiation_node,
            "dismissal": dismissal_node
        },
        aliases=["robber", "bandit", "rogue", "thief"],
        attributes={
            "moveable": True,
            "hostile": True,  
            "canonical": True,
            "steals_objects": True,
            "drops_loot_on_death": True,
            "movement_behavior": "roaming"
        },
        combat_stats=thief_combat_stats
    )
    
    # Initialize Thief behavior system
    thief.thief_behavior = ThiefBehavior(thief)
    
    return thief


def integrate_thief_behaviors(game_engine):
    """Integrate Thief behaviors into the game engine."""
    
    original_process_command = game_engine._process_command
    
    def enhanced_process_command(user_input: str) -> None:
        """Enhanced command processing with Thief behavior integration."""
        
        # Check for Thief theft attempts before processing player command
        thief = game_engine.npc_manager.get_npc("THIEF")
        if thief and thief.location == game_engine.player.current_room:
            _handle_thief_behaviors(game_engine, thief)
        
        # Process the original command
        original_process_command(user_input)
        
        # Check for Thief movement after player action  
        if thief and thief.get_attribute("moveable", False):
            _handle_thief_movement(game_engine, thief)
    
    game_engine._process_command = enhanced_process_command


def _handle_thief_behaviors(game_engine, thief: NPC):
    """Handle Thief theft attempts when in same room as player."""
    if not hasattr(thief, 'thief_behavior'):
        return
        
    behavior = thief.thief_behavior
    
    # Check for theft attempt
    stolen_item = behavior.attempt_theft(
        game_engine.player.inventory,
        game_engine.object_manager
    )
    
    if stolen_item:
        # Remove from player inventory
        game_engine.player.remove_from_inventory(stolen_item)
        
        # Get object name for message
        obj = game_engine.object_manager.get_object(stolen_item)
        item_name = obj.name if obj else "something"
        
        print(f"\\nThe thief quickly snatches your {item_name} and grins wickedly!")
        print("\"Thank you for the donation!\" The thief laughs.")


def _handle_thief_movement(game_engine, thief: NPC):
    """Handle Thief movement between rooms."""
    if not hasattr(thief, 'thief_behavior'):
        return
        
    behavior = thief.thief_behavior
    
    if not behavior.can_move():
        return
        
    # Get possible destinations
    destinations = behavior.get_movement_destinations(
        thief.location,
        game_engine.world
    )
    
    if not destinations:
        return
        
    # 30% chance to move each turn
    if random.random() < 0.3:
        new_room = random.choice(destinations)
        
        # Notify player if Thief was in their room
        if thief.location == game_engine.player.current_room:
            print("\\nThe thief slips away into the shadows.")
            
        # Move Thief
        old_location = thief.location
        game_engine.npc_manager.move_npc(thief.id, new_room)
        thief.location = new_room
        behavior.movement_timer = time.time()
        
        # Notify player if Thief enters their room
        if new_room == game_engine.player.current_room:
            print(f"\\n{thief.description}")


def handle_thief_combat_integration(game_engine, thief: NPC):
    """Handle special Thief combat behaviors."""
    
    # Override standard NPC death handling to drop loot
    original_handle_attack = game_engine._handle_attack
    
    def enhanced_handle_attack(command):
        result = original_handle_attack(command)
        
        # Check if Thief was defeated
        if (hasattr(thief, 'thief_behavior') and 
            not thief.combat_stats.is_alive()):
            
            behavior = thief.thief_behavior
            loot = behavior.drop_loot_on_death()
            
            if loot:
                current_room = game_engine.world.get_room(game_engine.player.current_room)
                print("\\nThe thief's possessions scatter as he falls:")
                
                for item_id in loot:
                    obj = game_engine.object_manager.get_object(item_id)
                    if obj and current_room:
                        current_room.add_item(item_id)
                        print(f"  A {obj.name} clatters to the ground.")
        
        return result
    
    game_engine._handle_attack = enhanced_handle_attack