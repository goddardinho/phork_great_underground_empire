"""
Object Combination and Transformation System for Zork

Implements authentic object interaction mechanics including combinations,
transformations, tool usage, and multi-object commands based on original MIT Zork.
"""

from typing import Dict, List, Optional, Callable, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """Types of object interactions."""
    COMBINE = "combine"  # Two objects create a new object
    TRANSFORM = "transform"  # One object changes into another
    APPLY_TOOL = "apply_tool"  # Use one object as a tool on another
    POUR_ON = "pour_on"  # Pour one object onto another
    BREAK_WITH = "break_with"  # Break object with another object
    LIGHT_WITH = "light_with"  # Light object using another object
    HEAT_WITH = "heat_with"  # Heat object using another object
    COOL_WITH = "cool_with"  # Cool object using another object


@dataclass
class InteractionRule:
    """Defines how two objects can interact."""
    id: str
    interaction_type: InteractionType
    primary_object: str  # The main object being acted upon
    secondary_object: Optional[str] = None  # Tool/reagent object (None for single-object transformations)
    required_room: Optional[str] = None  # Must be in specific room
    required_conditions: List[Callable] = field(default_factory=list)  # Custom conditions
    result_object: Optional[str] = None  # Object created/transformed to
    result_message: str = ""
    failure_message: str = ""
    consumes_primary: bool = False  # Whether primary object is destroyed
    consumes_secondary: bool = False  # Whether secondary object is destroyed
    score_reward: int = 0
    repeatable: bool = True  # Can interaction be repeated?


@dataclass
class ObjectState:
    """Tracks the current state of an object that can transform."""
    object_id: str
    current_form: str  # Current object ID 
    possible_states: Dict[str, str] = field(default_factory=dict)  # state_name -> object_id
    transformation_history: List[str] = field(default_factory=list)
    is_permanent: bool = False  # Whether transformations are reversible


class ObjectCombinationManager:
    """Manages object combinations, transformations, and tool usage."""
    
    def __init__(self):
        self.interaction_rules: Dict[str, InteractionRule] = {}
        self.object_states: Dict[str, ObjectState] = {}
        self.interaction_history: List[str] = []
        
        # Initialize canonical Zork interactions
        self._create_canonical_interactions()
    
    def _create_canonical_interactions(self) -> None:
        """Create authentic Zork object interactions."""
        
        # Bell transformation (becomes hot when heated)
        self.add_interaction_rule(InteractionRule(
            id="heat_bell",
            interaction_type=InteractionType.HEAT_WITH,
            primary_object="BELL",
            secondary_object="TORCH",  # Or any light source
            result_object="HBELL",  # Hot bell
            result_message="The bell becomes red hot!",
            failure_message="You need a heat source to heat the bell.",
            consumes_primary=True,
            score_reward=5
        ))
        
        # Wire/fuse with explosives
        self.add_interaction_rule(InteractionRule(
            id="fuse_explosive",
            interaction_type=InteractionType.COMBINE,
            primary_object="FUSE",
            secondary_object="EXPLOSIVE",  # Hypothetical explosive object
            result_object="ARMED_EXPLOSIVE",
            result_message="You carefully attach the fuse to the explosive.",
            failure_message="That's far too dangerous without proper equipment.",
            consumes_primary=True,
            consumes_secondary=True,
            score_reward=10
        ))
        
        # Tool usage - Pick/pry with tools
        self.add_interaction_rule(InteractionRule(
            id="pry_with_crowbar",
            interaction_type=InteractionType.APPLY_TOOL,
            primary_object="WOODEN_BOX",  # Can be pried open
            secondary_object="CROWBAR",
            result_message="You pry open the box with the crowbar.",
            failure_message="You need something to pry it open with."
        ))
        
        # Break mirror (authentic Zork action)
        self.add_interaction_rule(InteractionRule(
            id="break_mirror",
            interaction_type=InteractionType.BREAK_WITH,
            primary_object="MIRROR",
            secondary_object="RUSTY_KNIFE",  # Or any weapon
            result_object="BROKEN_MIRROR",
            result_message="The mirror shatters into many pieces. Seven years bad luck!",
            failure_message="The mirror is too tough to break with your bare hands.",
            consumes_primary=True,
            score_reward=-5  # Bad luck!
        ))
        
        # Light torch with matches (enhanced from existing light system)
        self.add_interaction_rule(InteractionRule(
            id="light_torch",
            interaction_type=InteractionType.LIGHT_WITH,
            primary_object="TORCH",
            secondary_object="MATCHES",
            result_message="You light the torch with a match. It burns brightly.",
            failure_message="You need matches or another flame source.",
            consumes_secondary=False  # Matches have limited uses but aren't destroyed per use
        ))
        
        # Pour oil on machinery (hypothetical maintenance action)
        self.add_interaction_rule(InteractionRule(
            id="oil_machinery",
            interaction_type=InteractionType.POUR_ON, 
            primary_object="MACHINERY",
            secondary_object="OIL_BOTTLE",
            result_message="You pour oil on the machinery. It begins running smoothly.",
            failure_message="The machinery needs lubrication.",
            consumes_secondary=True,
            score_reward=15
        ))
        
        # Combine rope with hook (classic adventure game combination)
        self.add_interaction_rule(InteractionRule(
            id="rope_and_hook",
            interaction_type=InteractionType.COMBINE,
            primary_object="ROPE",
            secondary_object="HOOK",
            result_object="GRAPPLING_HOOK",
            result_message="You tie the rope to the hook, creating a grappling hook.",
            failure_message="Those don't seem to go together.",
            consumes_primary=True,
            consumes_secondary=True,
            score_reward=10
        ))
    
    def add_interaction_rule(self, rule: InteractionRule) -> None:
        """Add a new interaction rule."""
        self.interaction_rules[rule.id] = rule
        logger.info(f"Added interaction rule: {rule.id}")
    
    def can_interact(self, primary_id: str, secondary_id: Optional[str] = None, 
                    command_verb: str = "", room_id: Optional[str] = None) -> Optional[InteractionRule]:
        """Check if objects can interact and return the applicable rule."""
        
        for rule in self.interaction_rules.values():
            # Check if objects match
            if rule.primary_object != primary_id:
                continue
                
            if rule.secondary_object and rule.secondary_object != secondary_id:
                continue
            
            # Check room requirement
            if rule.required_room and rule.required_room != room_id:
                continue
                
            # Check custom conditions
            if rule.required_conditions:
                try:
                    if not all(condition() for condition in rule.required_conditions):
                        continue
                except Exception as e:
                    logger.warning(f"Condition check failed for rule {rule.id}: {e}")
                    continue
            
            # Check if interaction type matches command verb (optional)
            if command_verb:
                verb_mapping = {
                    "combine": [InteractionType.COMBINE],
                    "heat": [InteractionType.HEAT_WITH],
                    "cool": [InteractionType.COOL_WITH],
                    "light": [InteractionType.LIGHT_WITH],
                    "break": [InteractionType.BREAK_WITH],
                    "pour": [InteractionType.POUR_ON],
                    "use": [InteractionType.APPLY_TOOL],
                    "apply": [InteractionType.APPLY_TOOL]
                }
                
                if command_verb.lower() in verb_mapping:
                    if rule.interaction_type not in verb_mapping[command_verb.lower()]:
                        continue
            
            return rule
        
        return None
    
    def perform_interaction(self, primary_id: str, secondary_id: Optional[str] = None,
                          command_verb: str = "", room_id: Optional[str] = None,
                          game_objects: Optional[Dict] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Perform object interaction.
        
        Returns: (success, message, result_object_id)
        """
        
        # Find applicable rule
        rule = self.can_interact(primary_id, secondary_id, command_verb, room_id)
        if not rule:
            return False, "Those objects don't seem to work together.", None
        
        # Check if rule has been used and is non-repeatable
        if not rule.repeatable and rule.id in self.interaction_history:
            return False, "You've already done that.", None
        
        # Record interaction
        self.interaction_history.append(rule.id)
        
        # Handle object state changes
        result_object = None
        if rule.result_object:
            result_object = rule.result_object
            
            # Update object states if transformation occurred
            if rule.interaction_type in [InteractionType.TRANSFORM, InteractionType.HEAT_WITH, 
                                      InteractionType.COOL_WITH, InteractionType.BREAK_WITH]:
                self._update_object_state(primary_id, result_object)
        
        logger.info(f"Performed interaction: {rule.id} ({primary_id} + {secondary_id})")
        
        return True, rule.result_message, result_object
    
    def _update_object_state(self, original_id: str, new_id: str) -> None:
        """Update object state tracking for transformations."""
        if original_id not in self.object_states:
            self.object_states[original_id] = ObjectState(
                object_id=original_id,
                current_form=original_id
            )
        
        state = self.object_states[original_id]
        state.transformation_history.append(new_id)
        state.current_form = new_id
    
    def get_object_state(self, object_id: str) -> Optional[ObjectState]:
        """Get current state of an object."""
        return self.object_states.get(object_id)
    
    def get_available_interactions(self, object_id: str) -> List[InteractionRule]:
        """Get all possible interactions for an object."""
        interactions = []
        for rule in self.interaction_rules.values():
            if rule.primary_object == object_id or rule.secondary_object == object_id:
                interactions.append(rule)
        return interactions
    
    def get_interaction_hints(self, object_id: str) -> List[str]:
        """Get hints about what interactions are possible with an object."""
        hints = []
        interactions = self.get_available_interactions(object_id)
        
        for rule in interactions:
            if rule.primary_object == object_id:
                if rule.secondary_object:
                    hints.append(f"Try using it with {rule.secondary_object.lower().replace('_', ' ')}")
                else:
                    hints.append(f"Try {rule.interaction_type.value.replace('_', ' ')}ing it")
            elif rule.secondary_object == object_id:
                hints.append(f"Try using it on {rule.primary_object.lower().replace('_', ' ')}")
        
        return hints
    
    def restore_interaction_state(self, state_data: Dict[str, Any]) -> None:
        """Restore interaction manager state from saved data."""
        self.interaction_history = state_data.get("interaction_history", [])
        
        # Restore object states
        states_data = state_data.get("object_states", {})
        for obj_id, state_info in states_data.items():
            self.object_states[obj_id] = ObjectState(
                object_id=state_info["object_id"],
                current_form=state_info["current_form"],
                transformation_history=state_info.get("transformation_history", []),
                is_permanent=state_info.get("is_permanent", False)
            )
    
    def save_interaction_state(self) -> Dict[str, Any]:
        """Save interaction manager state for persistence."""
        states_data = {}
        for obj_id, state in self.object_states.items():
            states_data[obj_id] = {
                "object_id": state.object_id,
                "current_form": state.current_form,
                "transformation_history": state.transformation_history,
                "is_permanent": state.is_permanent
            }
        
        return {
            "interaction_history": self.interaction_history,
            "object_states": states_data
        }


def integrate_combinations_into_game(game_engine):
    """Integrate object combination system into the main game engine."""
    game_engine.combination_manager = ObjectCombinationManager()
    
    # Add enhanced command handlers to GameEngine
    # These would be added to the _route_command method
    enhanced_handlers = {
        "heat": "_handle_heat",
        "cool": "_handle_cool", 
        "combine": "_handle_combine",
        "break": "_handle_break_with",
        "pour": "_handle_pour_on",
        "apply": "_handle_apply_tool",
        "use": "_handle_use_tool"
    }
    
    return game_engine.combination_manager