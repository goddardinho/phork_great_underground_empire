"""
Cyclops NPC implementation for Phork.
Based on original Zork I Cyclops with authentic behavior patterns.
"""

import random
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .npc import NPC
from .npc_manager import NPCManager
from .combat import CombatStats


@dataclass
class CyclopsState:
    """Tracks Cyclops-specific state information."""
    is_sleeping: bool = False
    wrath_level: int = 0  # Negative = less wrathful, positive = more wrathful
    last_fed_time: Optional[float] = None
    last_given_drink_time: Optional[float] = None
    times_attacked: int = 0
    has_been_awakened: bool = False


class CyclopsBehavior:
    """Manages Cyclops-specific behaviors including sleep/wake states, feeding, and staircase blocking."""
    
    def __init__(self, npc: NPC):
        self.npc = npc
        self.state = CyclopsState(is_sleeping=True)  # Starts sleeping like original
        
        # Food preferences (affects wrath reduction)
        self.food_preferences = {
            'food': 3,      # Generic food reduces wrath by 3
            'bread': 3,     # Bread is good food
            'garlic': -1,   # Garlic increases wrath (he doesn't like it)
            'lunch': 4,     # Lunch is especially good
            'meat': 4,      # Meat is preferred
            'sandwich': 3,  # Sandwiches are decent
            'apple': 2,     # Fruit is okay
            'fruit': 2      # Generic fruit
        }
        
        # Drinks that can make cyclops sleep
        self.sleep_drinks = {
            'water': True,
            'bottle': True,  # If bottle contains water
            'drink': True,   # Generic drink
            'potion': True   # Magic potion
        }
    
    def is_blocking_passage(self) -> bool:
        """Check if Cyclops is currently blocking passage."""
        return not self.state.is_sleeping and self.state.wrath_level >= 0
    
    def can_accept_food(self, food_name: str) -> bool:
        """Check if Cyclops will accept the offered food."""
        return food_name.lower() in self.food_preferences
    
    def give_food(self, food_name: str, player, object_manager) -> str:
        """Handle giving food to the Cyclops."""
        food_lower = food_name.lower()
        
        if not self.can_accept_food(food_lower):
            if food_lower == 'garlic':
                return "The cyclops may be hungry, but there is a limit."
            return "The cyclops is not so stupid as to eat THAT!"
        
        # Find and remove food from player's inventory
        food_item = None
        for item_id in player.inventory[:]:  # Copy to avoid modification during iteration
            item = object_manager.get_object(item_id)
            if item and food_name.lower() in item.name.lower():
                food_item = item
                player.remove_from_inventory(item_id)
                break
        
        if not food_item:
            return f"You don't have any {food_name}."
        
        # Reduce wrath based on food preference
        wrath_reduction = self.food_preferences[food_lower]
        old_wrath = self.state.wrath_level
        self.state.wrath_level = max(-5, self.state.wrath_level - wrath_reduction)
        self.state.last_fed_time = time.time()
        
        # Generate response based on wrath change
        if self.state.wrath_level <= -2:
            return (f"The cyclops devours the {food_item.name} hungrily and looks much more "
                   f"satisfied. He nods approvingly and steps aside slightly.")
        elif self.state.wrath_level < old_wrath:
            return (f"The cyclops eats the {food_item.name} and looks somewhat less "
                   f"menacing, though he still eyes you suspiciously.")
        else:
            return (f"The cyclops reluctantly accepts the {food_item.name} but doesn't "
                   f"seem very impressed.")
    
    def give_drink(self, drink_name: str, player, object_manager) -> str:
        """Handle giving drink to the Cyclops."""
        drink_lower = drink_name.lower()
        
        if drink_lower not in self.sleep_drinks:
            return "The cyclops sniffs the drink suspiciously and refuses it."
        
        if self.state.wrath_level > 0:
            return "The cyclops apparently is not thirsty and refuses your generosity."
        
        # Find and remove drink from player's inventory
        drink_item = None
        for item_id in player.inventory[:]:  # Copy to avoid modification during iteration
            item = object_manager.get_object(item_id)
            if item and drink_name.lower() in item.name.lower():
                drink_item = item
                player.remove_from_inventory(item_id)
                break
        
        if not drink_item:
            return f"You don't have any {drink_name}."
        
        # Make cyclops fall asleep
        self._fall_asleep()
        self.state.last_given_drink_time = time.time()
        
        return ("The cyclops looks tired and quickly falls fast asleep "
               "(what did you put in that drink, anyway?).")
    
    def wake_up(self, reason: str = "disturbed") -> str:
        """Wake up the Cyclops."""
        if not self.state.is_sleeping:
            return "The cyclops is already awake and glaring at you."
        
        self.state.is_sleeping = False
        self.state.has_been_awakened = True
        self.state.wrath_level = abs(self.state.wrath_level)  # Waking up makes wrath positive
        self.state.times_attacked += 1
        
        return "The cyclops yawns and stares at the thing that woke him up."
    
    def _fall_asleep(self):
        """Make the Cyclops fall asleep."""
        self.state.is_sleeping = True
        # When sleeping, wrath becomes less of an issue
        if self.state.wrath_level > 0:
            self.state.wrath_level = -abs(self.state.wrath_level)
    
    def handle_attack(self) -> str:
        """Handle being attacked (wakes up if sleeping, increases wrath)."""
        if self.state.is_sleeping:
            wake_response = self.wake_up("attacked")
            return f"{wake_response} The cyclops looks very angry about being awakened this way!"
        
        self.state.wrath_level += 2
        self.state.times_attacked += 1
        
        responses = [
            "The cyclops ignores all injury to his body with a shrug.",
            "The cyclops seems barely affected by your attack.",
            "Your attack bounces harmlessly off the cyclops's thick hide."
        ]
        return random.choice(responses)
    
    def get_status_description(self) -> str:
        """Get current status description of the Cyclops."""
        if self.state.is_sleeping:
            return ("The cyclops is slumped in the corner, snoring loudly. "
                   "His massive chest rises and falls rhythmically.")
        elif self.state.wrath_level <= -3:
            return ("The cyclops stands calmly in the corner, looking satisfied "
                   "and much less threatening than before.")
        elif self.state.wrath_level <= 0:
            return ("The cyclops is standing in the corner, eyeing you with "
                   "mild curiosity rather than hostility.")
        else:
            return ("A cyclops, who looks prepared to eat horses (much less mere "
                   "adventurers), blocks the staircase. From his state of health, and "
                   "the bloodstains on the walls, you gather that he is not very "
                   "friendly, though he likes people.")
    
    def get_blocking_message(self) -> str:
        """Get message for when Cyclops blocks movement.""" 
        if self.state.is_sleeping:
            return None  # Sleeping cyclops doesn't block
        
        if self.state.wrath_level <= -2:
            return None  # Satisfied cyclops lets you pass
        
        return ("The cyclops blocks your path, glaring menacingly. "
               "Perhaps you should try offering him something, or find "
               "another way to deal with him.")


def create_canonical_cyclops() -> NPC:
    """Create the canonical Cyclops NPC for Zork."""
    
    # Create combat stats (very strong, stronger than Troll)
    combat_stats = CombatStats(
        max_health=300,
        current_health=300, 
        attack_power=40,
        defense=15,
        weapon=None  # Uses fists
    )
    
    # Create NPC
    cyclops = NPC(
        id="CYCLOPS",
        name="cyclops",
        description="A cyclops, who looks prepared to eat horses (much less mere adventurers), blocks the staircase.",
        location="CYCLO",
        combat_stats=combat_stats
    )
    
    # Add aliases
    cyclops.aliases.extend(["giant", "monster", "creature", "cyclo"])
    
    # Mark as canonical
    cyclops.set_attribute("canonical", True)
    cyclops.set_attribute("blocks_exits", ["up"])  # Blocks staircase
    
    # Set up dialogue options
    from .npc import DialogueNode
    cyclops.dialogue_tree = {
        'default': DialogueNode('default', "The cyclops stares at you with his single enormous eye."),
        'greeting': DialogueNode('greeting', "The cyclops grunts acknowledgment but continues to block your path."),
        'threats': DialogueNode('threats', "'Do you think I'm as stupid as my father was?', he says."),
        'hungry': DialogueNode('hungry', "The cyclops looks extremely hungry, even for a cyclops.")
    }
    
    return cyclops


def integrate_cyclops_behaviors(game_engine, npc_manager: NPCManager):
    """Integrate Cyclops behaviors into the game engine."""
    
    cyclops = npc_manager.get_npc("CYCLOPS")
    if not cyclops:
        return
    
    behavior = CyclopsBehavior(cyclops)
    cyclops.set_attribute("behavior", behavior)
    
    # Store original movement method
    if not hasattr(game_engine, '_original_handle_movement_cyclops'):
        game_engine._original_handle_movement_cyclops = game_engine._handle_movement
    
    def cyclops_movement_wrapper(self, direction: str) -> None:
        """Wrapper that checks Cyclops blocking before movement."""
        current_room = self.world.get_room(self.player.current_room)
        
        # Check if we're in the Cyclops room and trying to go up
        if (current_room and current_room.id == "CYCLO" and 
            direction.lower() in ["up", "u"]):
            
            cyclops_npc = self.npc_manager.get_npc("CYCLOPS")
            if cyclops_npc and cyclops_npc.location == current_room.id:
                cyclops_behavior = cyclops_npc.get_attribute("behavior")
                if cyclops_behavior and cyclops_behavior.is_blocking_passage():
                    blocking_msg = cyclops_behavior.get_blocking_message()
                    if blocking_msg:
                        print(blocking_msg)
                        return  # Block the movement
        
        # Use original movement logic
        self._original_handle_movement_cyclops(direction)
    
    # Replace method
    import types
    game_engine._handle_movement = types.MethodType(cyclops_movement_wrapper, game_engine)
    
    # Store original command processor
    if not hasattr(game_engine, '_original_process_command_cyclops'):
        game_engine._original_process_command_cyclops = game_engine._process_command
    
    def cyclops_command_wrapper(self, command: str) -> str:
        """Wrapper that handles Cyclops-specific commands."""
        parts = command.strip().lower().split()
        if not parts:
            return self._original_process_command_cyclops(command)
        
        verb = parts[0]
        
        # Handle giving items to cyclops
        if verb == "give" and len(parts) >= 3:
            if "cyclops" in command.lower() or "cyclo" in command.lower():
                return handle_give_to_cyclops(self, command, parts)
        
        # Handle wake/attack cyclops commands
        if verb in ["wake", "kick", "attack", "hit", "poke"] and len(parts) >= 2:
            if any(target in command.lower() for target in ["cyclops", "cyclo", "giant", "monster"]):
                return handle_cyclops_interaction(self, verb, command)
        
        # Use original command processing
        return self._original_process_command_cyclops(command)
    
    # Replace method
    game_engine._process_command = types.MethodType(cyclops_command_wrapper, game_engine)


def handle_give_to_cyclops(game_engine, command: str, parts: list) -> str:
    """Handle giving items to the Cyclops."""
    cyclops = game_engine.npc_manager.get_npc("CYCLOPS")
    if not cyclops:
        return "There's no cyclops here."
    
    current_room = game_engine.world.get_room(game_engine.player.current_room)
    if not current_room or cyclops.location != current_room.id:
        return "There's no cyclops here."
    
    behavior = cyclops.get_attribute("behavior")
    if not behavior:
        return "The cyclops doesn't seem to be responding."
    
    # Parse what item is being given
    # Command like "give food to cyclops" or "give cyclops food"
    item_name = None
    if len(parts) >= 4 and parts[2] == "to":
        item_name = parts[1]  # "give ITEM to cyclops"
    elif len(parts) >= 3:
        # Could be "give cyclops ITEM" 
        if parts[1] in ["cyclops", "cyclo", "giant", "monster"]:
            if len(parts) > 2:
                item_name = " ".join(parts[2:])
        else:
            item_name = parts[1]  # "give ITEM cyclops"
    
    if not item_name:
        return "Give what to the cyclops?"
    
    # Check if player has the item
    player = game_engine.player
    has_item = False
    for item_id in player.inventory:
        item = game_engine.object_manager.get_object(item_id)
        if item and item_name.lower() in item.name.lower():
            has_item = True
            break
    
    if not has_item:
        return f"You don't have a {item_name}."
    
    # Check if it's food or drink
    item_lower = item_name.lower()
    
    # Check drinks first (water, bottle, etc.)
    if any(drink in item_lower for drink in ['water', 'bottle', 'drink', 'potion']):
        return behavior.give_drink(item_name, player, game_engine.object_manager)
    
    # Check foods
    if (any(food in item_lower for food in ['food', 'bread', 'lunch', 'meat', 'sandwich', 'apple', 'fruit']) or
        'garlic' in item_lower):
        return behavior.give_food(item_name, player, game_engine.object_manager)
    
    return "The cyclops is not so stupid as to eat THAT!"


def handle_cyclops_interaction(game_engine, verb: str, command: str) -> str:
    """Handle wake/attack/poke cyclops commands."""
    cyclops = game_engine.npc_manager.get_npc("CYCLOPS") 
    if not cyclops:
        return "There's no cyclops here."
    
    current_room = game_engine.world.get_room(game_engine.player.current_room)
    if not current_room or cyclops.location != current_room.id:
        return "There's no cyclops here."
    
    behavior = cyclops.get_attribute("behavior")
    if not behavior:
        return "The cyclops doesn't seem to be responding."
    
    if verb in ["wake", "kick"]:
        if behavior.state.is_sleeping:
            return behavior.wake_up("disturbed")
        else:
            return "The cyclops is already awake."
    
    elif verb == "poke":
        if behavior.state.is_sleeping:
            return behavior.wake_up("poked")
        else:
            return "'Do you think I'm as stupid as my father was?', he says, dodging."
    
    elif verb in ["attack", "hit"]:
        # This triggers combat, but also handles waking
        response = behavior.handle_attack()
        
        # If cyclops is now awake and aggressive, initiate combat
        if not behavior.state.is_sleeping and behavior.state.wrath_level > 0:
            # Let the combat system handle the actual combat
            combat_response = game_engine.combat_manager.initiate_combat(
                game_engine.player, cyclops
            )
            return f"{response}\n\n{combat_response}"
        
        return response
    
    return "I don't understand that action with the cyclops."


# Combat integration for Cyclops-specific messages
CYCLOPS_COMBAT_MESSAGES = {
    'miss_attacker': [
        "The Cyclops misses, but the backwash almost knocks you over.",
        "The Cyclops rushes you, but runs into the wall.", 
        "The Cyclops trips over his feet trying to get at you.",
        "The Cyclops unleashes a roundhouse punch, but you have time to dodge."
    ],
    'kill_attacker': [
        "The Cyclops knocks you unconscious.",
        "The Cyclops sends you crashing to the floor, unconscious."
    ],
    'death_attacker': [
        "The Cyclops raises his arms and crushes your skull.",
        "The Cyclops has just essentially ripped you to shreds.",
        "The Cyclops decks you. In fact, you are dead.",
        "The Cyclops breaks your neck with a massive smash."
    ],
    'light_wound_attacker': [
        "A quick punch, but it was only a glancing blow.",
        "The Cyclops grabs but you twist free, leaving part of your cloak.",
        "A glancing blow from the Cyclops' fist.",
        "The Cyclops chops at you with the side of his hand, and it connects, but not solidly."
    ],
    'serious_wound_attacker': [
        "The Cyclops gets a good grip and breaks your arm.",
        "The monster smashes his huge fist into your chest, breaking several ribs.",
        "The Cyclops almost knocks the wind out of you with a quick punch.",
        "A flying drop kick breaks your jaw.",
        "The Cyclops breaks your leg with a staggering blow."
    ],
    'knockout_attacker': [
        "The Cyclops knocks you silly, and you reel back.",
        "The Cyclops lands a punch that knocks the wind out of you.",
        "Heedless of your weapons, the Cyclops tosses you against the rock wall of the room.",
        "The Cyclops grabs you, and almost strangles you before you wiggle free, breathless."
    ]
}