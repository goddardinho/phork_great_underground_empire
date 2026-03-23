"""Troll NPC Implementation - Phase 3 of Canonical NPCs Feature

The Troll is a canonical NPC from original Zork, featuring:
- Bridge/passage blocking behavior (blocks all room exits when active)
- Payment/toll negotiation (accepts gifts to allow passage)
- Combat integration with enhanced axe weapon
- Room state management (unconscious state opens passages)
- Authentic Zork Troll interactions and responses

This implementation builds on the foundation established by the Thief NPC
and provides the classic bridge-guarding challenge from original Zork.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import random
import time

from .npc import NPC, DialogueNode, DialogueResponse
from .combat import CombatStats
from .objects import GameObject


class TrollBehavior:
    """Manages Troll-specific behaviors and mechanics."""
    
    def __init__(self, troll_npc: NPC):
        self.troll = troll_npc
        self.accepted_payments: List[str] = []  # Items given to troll
        self.is_blocking_passage = True  # Whether troll blocks exits
        self.last_payment_time = 0
        self.payment_satisfaction_duration = 300  # 5 minutes
        
        # Troll preferences for items (what it likes as payment)
        self.payment_preferences = {
            "food": 10,      # Highest priority - troll loves food!
            "treasure": 8,   # High value items are appreciated
            "weapon": 6,     # Weapons interest the troll
            "shiny": 5,      # Shiny objects catch its attention  
            "tool": 3,       # Tools have some value
            "other": 1       # Everything else has minimal appeal
        }
    
    def is_satisfied_with_payment(self) -> bool:
        """Check if troll has been recently paid and is satisfied."""
        if not self.accepted_payments:
            return False
            
        current_time = time.time()
        return (current_time - self.last_payment_time) < self.payment_satisfaction_duration
    
    def should_block_passage(self) -> bool:
        """Determine if troll should block room exits."""
        # If troll is unconscious/dead, it can't block
        if self.troll.combat_stats and self.troll.combat_stats.current_health <= 0:
            return False
            
        # If recently satisfied with payment, allow passage
        if self.is_satisfied_with_payment():
            return False
            
        return self.is_blocking_passage
    
    def evaluate_payment_item(self, item_id: str, object_manager) -> int:
        """Evaluate how much troll likes an item as payment. Returns priority score."""
        obj = object_manager.get_object(item_id)
        if not obj:
            return 0
            
        priority = 0
        item_name = obj.name.lower()
        
        # Check for food items (troll's favorite!)
        food_items = ["bread", "food", "meat", "cheese", "apple", "fruit", "meal", 
                     "sandwich", "cake", "pie", "snack", "pepper", "garlic"]
        if any(food in item_name for food in food_items):
            priority += self.payment_preferences["food"]
            
        # Check for treasure value
        if obj.get_attribute("treasure_value", 0) > 0:
            priority += self.payment_preferences["treasure"]
            
        # Check for weapons
        if obj.get_attribute("weapon", False) or any(weapon in item_name for weapon in ["sword", "knife", "axe", "club"]):
            priority += self.payment_preferences["weapon"]
            
        # Check for shiny objects
        if any(shiny in item_name for shiny in ["gold", "silver", "jewel", "gem", "coin", "mirror", "brass"]):
            priority += self.payment_preferences["shiny"]
            
        # Check for tools
        if obj.get_attribute("tool", False) or any(tool in item_name for tool in ["key", "lamp", "lantern", "rope"]):
            priority += self.payment_preferences["tool"]
        else:
            priority += self.payment_preferences["other"]
            
        return priority
    
    def accept_payment(self, item_id: str) -> str:
        """Accept an item as payment and return troll's response."""
        self.accepted_payments.append(item_id)
        self.last_payment_time = time.time()
        self.is_blocking_passage = False  # Temporarily allow passage
        
        # Return different responses based on item type
        responses = [
            "The troll grins wickedly and steps aside, allowing you to pass.",
            "The troll examines the gift carefully, then nods approvingly and moves away from the passages.",
            "The troll accepts your offering with a grunt and lumbers to one side.",
            "The troll clutches the item protectively and shuffles away from the exits."
        ]
        
        return random.choice(responses)
    
    def get_blocking_message(self) -> str:
        """Get message describing how troll blocks passage."""
        if not self.should_block_passage():
            return "An unconscious troll is sprawled on the floor. All passages out of the room are open."
        
        return "A nasty-looking troll, brandishing a bloody axe, blocks all passages out of the room."
    
    def handle_combat_victory(self) -> str:
        """Handle when troll is defeated in combat."""
        self.is_blocking_passage = False
        return "The troll collapses with a thunderous crash! All passages are now clear."
    
    def handle_combat_recovery(self) -> str:
        """Handle when troll recovers from being unconscious."""
        if self.troll.combat_stats and self.troll.combat_stats.current_health > 0:
            self.is_blocking_passage = True
            return "The troll stirs and rises to its feet, once again blocking all passages!"
        return ""


def create_canonical_troll(npc_manager, starting_room: str = "MTROL") -> NPC:
    """Create the canonical Troll NPC with authentic Zork behaviors."""
    
    # Create the Troll's axe weapon  
    troll_axe = GameObject(
        id="TROLL_AXE",
        name="bloody axe",
        description="A massive, double-bladed axe with dried blood coating the gleaming metal. It seems to radiate an ominous heat.",
        aliases=["axe", "weapon", "bloody", "troll's", "blade"],
        attributes={
            "takeable": False,  # Cannot be taken due to heat
            "weapon": True,
            "damage": 8,  # High damage weapon
            "weight": 5,
            "hot": True,  # Special property from original Zork
            "troll_weapon": True
        }
    )
    
    # Create dialogue nodes for Troll interactions
    encounter_node = DialogueNode(
        id="encounter",
        text="The massive troll blocks your path, brandishing a bloody axe. It grunts menacingly and points at your possessions, then at the blocked passages.",
        responses=[
            DialogueResponse(
                id="resp_fight",
                text="I'll fight you for passage!",
                next_node="combat_challenge"
            ),
            DialogueResponse(
                id="resp_negotiate",
                text="Perhaps I have something you'd like",
                next_node="negotiation"
            ),
            DialogueResponse(
                id="resp_retreat",
                text="I don't want trouble",
                next_node="dismissal"
            )
        ]
    )
    
    combat_challenge_node = DialogueNode(
        id="combat_challenge",
        text="The troll roars a deafening battle cry and raises its massive axe above its head. Its eyes gleam with bloodlust!",
        end_conversation=True
    )
    
    negotiation_node = DialogueNode(
        id="negotiation",
        text="The troll examines you with calculating eyes, then grunts and points again at your belongings. It seems willing to negotiate for passage.",
        responses=[
            DialogueResponse(
                id="resp_offer",
                text="I'll give you something valuable",
                next_node="payment_offer"
            ),
            DialogueResponse(
                id="resp_no_deal",
                text="I have nothing for you",
                next_node="payment_refused"
            )
        ]
    )
    
    payment_offer_node = DialogueNode(
        id="payment_offer",
        text="The troll nods eagerly and holds out one massive, grimy hand while keeping the axe ready in the other.",
        end_conversation=True
    )
    
    payment_refused_node = DialogueNode(
        id="payment_refused", 
        text="The troll snarls in disappointment and tightens its grip on the axe. It looks ready for violence.",
        end_conversation=True
    )
    
    dismissal_node = DialogueNode(
        id="dismissal",
        text="The troll watches you suspiciously as you back away, but makes no move to pursue. It remains firmly planted in front of all exits.",
        end_conversation=True
    )
    
    # Create Troll with powerful combat stats (stronger than thief)
    troll_combat_stats = CombatStats(
        max_health=150,     # Very tough
        current_health=150,
        attack_power=25,    # Stronger than thief
        defense=12,         # Well-armored
        accuracy=70,        # Decent but not as skilled as thief
        dodge_chance=10,    # Slow but powerful
        block_chance=25,    # Good at blocking with axe
        critical_chance=20,  # Devastating when it hits 
        weapon=troll_axe    # Equip the bloody axe
    )
    
    troll = NPC(
        id="TROLL",
        name="troll",
        description="A nasty-looking troll, brandishing a bloody axe, blocks all passages out of the room.",
        location=starting_room,
        dialogue_tree={
            "encounter": encounter_node,
            "combat_challenge": combat_challenge_node,
            "negotiation": negotiation_node,
            "payment_offer": payment_offer_node,
            "payment_refused": payment_refused_node,
            "dismissal": dismissal_node
        },
        aliases=["troll", "monster", "creature", "beast", "guard"],
        attributes={
            "moveable": False,  # Troll stays in its room
            "hostile": True,
            "canonical": True,
            "blocks_passages": True,
            "accepts_payments": True,
            "bridge_guardian": True,
            "weapon": "axe"
        },
        combat_stats=troll_combat_stats
    )
    
    # Initialize Troll behavior system
    troll.troll_behavior = TrollBehavior(troll)
    
    # Store reference to axe for special interactions
    troll.axe = troll_axe
    
    return troll


def integrate_troll_behaviors(game_engine):
    """Integrate Troll behaviors into the game engine."""
    
    original_handle_movement = game_engine._handle_movement
    
    def enhanced_handle_movement(direction: str) -> None:
        """Enhanced movement handling with Troll passage blocking."""
        
        # Check if troll is in current room and blocking passage
        troll = game_engine.npc_manager.get_npc("TROLL")
        
        if (troll and 
            troll.location == game_engine.player.current_room and 
            troll.troll_behavior.should_block_passage()):
            
            print("The troll blocks your way, brandishing its axe menacingly.")
            print("You cannot pass while the troll guards this room.")
            return
        
        # Process normal movement if troll allows
        original_handle_movement(direction)
    
    game_engine._handle_movement = enhanced_handle_movement
    
    # Also integrate payment handling
    original_process_command = game_engine._process_command
    
    def enhanced_process_command(user_input: str) -> None:
        """Enhanced command processing with Troll payment integration."""
        
        # Check for troll payment commands  
        troll = game_engine.npc_manager.get_npc("TROLL")
        if troll and troll.location == game_engine.player.current_room:
            if _handle_troll_payment_commands(game_engine, troll, user_input):
                return  # Command was handled by troll payment system
        
        # Process the original command
        original_process_command(user_input)
    
    # Also integrate axe special interactions
    original_handle_take = game_engine._handle_take
    
    def enhanced_handle_take(command) -> None:
        """Enhanced take handling with Troll axe special behavior."""
        
        # Check if trying to take troll's axe
        troll = game_engine.npc_manager.get_npc("TROLL")
        if (troll and 
            troll.location == game_engine.player.current_room and 
            command.noun and 
            "axe" in command.noun.lower()):
            
            print("The troll's axe seems white-hot. You can't hold on to it.")
            return
        
        # Process normal take command
        original_handle_take(command)
    
    game_engine._handle_take = enhanced_handle_take


def _handle_troll_payment_commands(game_engine, troll, user_input: str) -> bool:
    """Handle commands related to paying the troll. Returns True if command was handled."""
    
    tokens = user_input.lower().strip().split()
    if not tokens:
        return False
        
    verb = tokens[0]
    
    # Handle "give X to troll" or "give troll X"  
    if verb == "give" and len(tokens) >= 3 and "troll" in tokens:
        # Parse what item to give
        if tokens[2] == "troll":  # "give X to troll"
            item_name = tokens[1]
        elif tokens[1] == "troll": # "give troll X"
            item_name = tokens[2] if len(tokens) > 2 else ""
        else:
            return False
            
        return _process_troll_payment(game_engine, troll, item_name)
    
    # Handle "offer X" when troll is present
    elif verb == "offer" and len(tokens) >= 2:
        item_name = tokens[1]
        return _process_troll_payment(game_engine, troll, item_name)
    
    return False


def _process_troll_payment(game_engine, troll, item_name: str) -> bool:
    """Process giving an item to the troll as payment."""
    
    # Find the item in player's inventory
    item_obj = None
    item_id = None
    
    for obj_id in game_engine.player.inventory:
        obj = game_engine.object_manager.get_object(obj_id)
        if obj and (item_name.lower() in obj.name.lower() or 
                   item_name.lower() in [alias.lower() for alias in obj.aliases]):
            item_obj = obj
            item_id = obj_id
            break
    
    if not item_obj:
        print(f"You don't have a {item_name}.")
        return True
    
    # Evaluate how much troll likes this item
    priority = troll.troll_behavior.evaluate_payment_item(item_id, game_engine.object_manager)
    
    if priority < 3:  # Troll doesn't like this item
        print(f"The troll examines the {item_obj.name} and shakes its head dismissively.")
        print("It seems uninterested in your offering.")
        return True
    
    # Remove item from player and give to troll
    game_engine.player.inventory.remove(item_id)
    response = troll.troll_behavior.accept_payment(item_id)
    
    print(f"You give the {item_obj.name} to the troll.")
    print(response)
    
    # Special response for food items
    if priority >= 8:  # High priority items get special responses
        print("The troll seems very pleased with your gift!")
        if "food" in item_obj.name.lower() or any(food in item_obj.name.lower() for food in ["bread", "meat", "cheese"]):
            print("The troll devours the food immediately, making satisfied grunting noises.")
    
    return True


# Export the main functions for integration
__all__ = ['TrollBehavior', 'create_canonical_troll', 'integrate_troll_behaviors']