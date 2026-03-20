"""
Multi-Step Puzzle System for Zork

Implements authentic Zork-style puzzles with state management, scoring,
and complex multi-step interactions modeled after original MIT Zork.
"""

from typing import Dict, Any, Callable, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PuzzleState(Enum):
    """State of a puzzle."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"  
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PuzzleStep:
    """A single step in a multi-step puzzle."""
    id: str
    description: str
    trigger_condition: Callable[..., bool]  # Function to check if step can be triggered
    action: Callable[..., Any]  # Function to execute when step is triggered
    required_objects: List[str] = field(default_factory=list)  # Objects needed in inventory
    required_room: Optional[str] = None  # Specific room requirement
    required_flags: List[str] = field(default_factory=list)  # Game flags that must be set
    score_reward: int = 0
    completion_message: str = ""
    failure_message: str = ""


@dataclass  
class Puzzle:
    """A complete multi-step puzzle."""
    id: str
    name: str
    description: str
    steps: List[PuzzleStep] = field(default_factory=list)
    current_step: int = 0
    state: PuzzleState = PuzzleState.NOT_STARTED
    total_score: int = 0
    is_repeatable: bool = False  # Most Zork puzzles are one-time only
    completion_callback: Optional[Callable] = None  # Called when puzzle completes
    
    def is_complete(self) -> bool:
        """Check if puzzle is fully completed."""
        return self.state == PuzzleState.COMPLETED
        
    def is_failed(self) -> bool:
        """Check if puzzle has failed.""" 
        return self.state == PuzzleState.FAILED
        
    def get_current_step(self) -> Optional[PuzzleStep]:
        """Get the current step, or None if complete/failed."""
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def advance_step(self) -> bool:
        """Advance to next step. Returns True if puzzle completed."""
        self.current_step += 1
        if self.current_step >= len(self.steps):
            self.state = PuzzleState.COMPLETED
            if self.completion_callback:
                self.completion_callback(self)
            return True
        return False


class PuzzleManager:
    """Manages all puzzles and their states in the game."""
    
    def __init__(self, game_engine):
        self.game = game_engine
        self.puzzles: Dict[str, Puzzle] = {}
        self.global_flags: Dict[str, Any] = {}  # Game-wide puzzle flags
        self.completed_puzzles: List[str] = []
        self.total_puzzle_score = 0
        
    def register_puzzle(self, puzzle: Puzzle) -> None:
        """Register a new puzzle."""
        self.puzzles[puzzle.id] = puzzle
        logger.info(f"Registered puzzle: {puzzle.name} ({puzzle.id})")
        
    def get_puzzle(self, puzzle_id: str) -> Optional[Puzzle]:
        """Get a puzzle by ID."""
        return self.puzzles.get(puzzle_id)
        
    def set_flag(self, flag_name: str, value: Any = True) -> None:
        """Set a global puzzle flag."""
        self.global_flags[flag_name] = value
        logger.debug(f"Set puzzle flag: {flag_name} = {value}")
        
    def get_flag(self, flag_name: str, default: Any = False) -> Any:
        """Get a global puzzle flag value."""
        return self.global_flags.get(flag_name, default)
        
    def check_flag(self, flag_name: str) -> bool:
        """Check if a flag is set (truthy)."""
        return bool(self.get_flag(flag_name))
        
    def attempt_puzzle_action(self, command_verb: str, target_object: str = None, 
                            target_room: str = None, **kwargs) -> Tuple[bool, str]:
        """
        Attempt to trigger puzzle actions based on player command.
        Returns (success, message) tuple.
        """
        triggered_any = False
        result_message = ""
        
        # Check all active puzzles for potential triggers
        for puzzle in self.puzzles.values():
            if puzzle.is_complete() or puzzle.is_failed():
                continue
                
            current_step = puzzle.get_current_step()
            if not current_step:
                continue
                
            # Check if this command could trigger the current step
            if self._can_trigger_step(puzzle, current_step, command_verb, 
                                    target_object, target_room, **kwargs):
                success, message = self._execute_puzzle_step(puzzle, current_step, **kwargs)
                if success:
                    triggered_any = True
                    if message:
                        result_message += message + " "
                        
        return triggered_any, result_message.strip()
        
    def _can_trigger_step(self, puzzle: Puzzle, step: PuzzleStep, 
                         command_verb: str, target_object: str = None,
                         target_room: str = None, **kwargs) -> bool:
        """Check if a puzzle step can be triggered by current game state."""
        
        # Check room requirement
        if step.required_room:
            current_room = self.game.player.current_room
            if current_room != step.required_room:
                return False
                
        # Check required objects in inventory
        player_inventory = set(self.game.player.inventory)
        required_objects = set(step.required_objects)
        if not required_objects.issubset(player_inventory):
            return False
            
        # Check required flags
        for flag in step.required_flags:
            if not self.check_flag(flag):
                return False
                
        # Execute the step's trigger condition
        try:
            return step.trigger_condition(
                game=self.game,
                command_verb=command_verb,
                target_object=target_object,
                target_room=target_room,
                puzzle_manager=self,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Error in puzzle trigger condition {step.id}: {e}")
            return False
            
    def _execute_puzzle_step(self, puzzle: Puzzle, step: PuzzleStep, **kwargs) -> Tuple[bool, str]:
        """Execute a puzzle step action."""
        try:
            # Execute the step action
            result = step.action(
                game=self.game,
                puzzle_manager=self,
                puzzle=puzzle,
                step=step,
                **kwargs
            )
            
            # Update puzzle state
            if puzzle.state == PuzzleState.NOT_STARTED:
                puzzle.state = PuzzleState.IN_PROGRESS
                
            # Add score if successful
            if result and step.score_reward > 0:
                self.total_puzzle_score += step.score_reward
                puzzle.total_score += step.score_reward
                
            # Advance puzzle step
            puzzle_completed = puzzle.advance_step()
            if puzzle_completed:
                self.completed_puzzles.append(puzzle.id)
                logger.info(f"Puzzle completed: {puzzle.name}")
                
            # Return appropriate message
            message = step.completion_message if result else step.failure_message
            return result, message
            
        except Exception as e:
            logger.error(f"Error executing puzzle step {step.id}: {e}")
            puzzle.state = PuzzleState.FAILED
            return False, step.failure_message or "Something went wrong."
            
    def get_puzzle_status(self) -> Dict[str, Any]:
        """Get status of all puzzles for debugging/save games."""
        return {
            "puzzles": {
                puzzle_id: {
                    "state": puzzle.state.value,
                    "current_step": puzzle.current_step,
                    "score": puzzle.total_score
                }
                for puzzle_id, puzzle in self.puzzles.items()
            },
            "flags": self.global_flags,
            "completed": self.completed_puzzles,
            "total_score": self.total_puzzle_score
        }
        
    def load_puzzle_status(self, status: Dict[str, Any]) -> None:
        """Load puzzle status from save data."""
        self.global_flags = status.get("flags", {})
        self.completed_puzzles = status.get("completed", [])
        self.total_puzzle_score = status.get("total_score", 0)
        
        puzzle_data = status.get("puzzles", {})
        for puzzle_id, data in puzzle_data.items():
            if puzzle_id in self.puzzles:
                puzzle = self.puzzles[puzzle_id]
                puzzle.state = PuzzleState(data["state"])
                puzzle.current_step = data["current_step"]
                puzzle.total_score = data["score"]


# ============================================================================
# PUZZLE REGISTRY - Authentic Zork Puzzle Implementations
# ============================================================================

def create_authentic_zork_puzzles(game_engine) -> PuzzleManager:
    """Create and configure all authentic Zork puzzles."""
    manager = PuzzleManager(game_engine)
    
    # Register core puzzles based on original Zork patterns
    manager.register_puzzle(_create_mailbox_puzzle())
    manager.register_puzzle(_create_grate_key_puzzle()) 
    manager.register_puzzle(_create_dam_control_puzzle())
    manager.register_puzzle(_create_treasure_collection_puzzle())
    
    return manager


def _create_mailbox_puzzle() -> Puzzle:
    """Simple tutorial puzzle - opening the mailbox."""
    
    def can_open_mailbox(game, command_verb, target_object, **kwargs):
        return (command_verb == "open" and 
                target_object and 
                target_object.lower() in ["mailbox", "box"] and
                "MAILBOX" in game.object_manager.get_all_objects())
    
    def open_mailbox_action(game, puzzle_manager, **kwargs):
        # Mailbox opening is handled by normal game mechanics
        # This just awards the puzzle score
        puzzle_manager.set_flag("mailbox_opened", True)
        return True
        
    step = PuzzleStep(
        id="open_mailbox",
        description="Open the mailbox to find the leaflet",
        trigger_condition=can_open_mailbox,
        action=open_mailbox_action,
        score_reward=5,
        completion_message="You have opened the mailbox! Welcome to Zork!",
        required_room="SHOUS"  # South of House
    )
    
    return Puzzle(
        id="mailbox_tutorial",
        name="Mailbox Discovery", 
        description="Learning to interact with objects",
        steps=[step]
    )


def _create_grate_key_puzzle() -> Puzzle:
    """Classic Zork grate unlocking sequence."""
    
    def has_keys_and_at_grate(game, command_verb, target_object, **kwargs):
        # Check if player has keys and is at the grate location
        has_keys = "KEYS" in game.player.inventory
        at_grate = game.player.current_room == "MGRAT"  # Grating Room
        is_unlock_cmd = command_verb == "unlock" and target_object and "grate" in target_object.lower()
        return has_keys and at_grate and is_unlock_cmd
    
    def unlock_grate_action(game, puzzle_manager, **kwargs):
        # Unlock the grate - modify room exits
        grate_room = game.world.get_room("MGRAT")  # Grating Room
        if grate_room:
            # Add new exit down to underground
            grate_room.exits["down"] = "CELLA"  # Connect to Cellar
            puzzle_manager.set_flag("grate_unlocked", True)
            return True
        return False
    
    # Step 1: Find the keys
    find_keys_step = PuzzleStep(
        id="find_keys",
        description="Find the rusty keys",  
        trigger_condition=lambda game, command_verb, target_object, **kwargs: (
            command_verb == "take" and target_object and "key" in target_object.lower()
        ),
        action=lambda **kwargs: True,
        score_reward=5,
        completion_message="The keys might be useful for unlocking something..."
    )
    
    # Step 2: Unlock the grate
    unlock_step = PuzzleStep(
        id="unlock_grate",
        description="Use keys to unlock the grate",
        trigger_condition=has_keys_and_at_grate,
        action=unlock_grate_action,
        required_objects=["KEYS"],
        required_room="MGRAT",
        score_reward=10,
        completion_message="The grate creaks open, revealing a dark passage below!",
        failure_message="The grate won't budge."
    )
    
    return Puzzle(
        id="grate_unlock",
        name="Grate Access",
        description="Unlock underground access with the rusty keys",
        steps=[find_keys_step, unlock_step]
    )


def _create_dam_control_puzzle() -> Puzzle:
    """Complex dam control puzzle with multiple switches."""
    
    def at_dam_control(game, **kwargs):
        return game.player.current_room == "DAM_CONTROL"  # Need to add this room
    
    def turn_bolt_trigger(game, command_verb, target_object, **kwargs):
        return (at_dam_control(game) and 
                command_verb in ["turn", "push", "press"] and
                target_object in ["bolt", "button", "switch"])
    
    def turn_bolt_action(game, puzzle_manager, **kwargs):
        # Toggle dam state
        current_state = puzzle_manager.get_flag("dam_gate_open", False)
        new_state = not current_state
        puzzle_manager.set_flag("dam_gate_open", new_state)
        
        # Modify connected rooms based on water level
        if new_state:
            # Dam open - water flows, reveals new areas
            puzzle_manager.set_flag("water_level_low", True)
            return True
        else:
            # Dam closed - water rises
            puzzle_manager.set_flag("water_level_low", False) 
            return True
    
    step = PuzzleStep(
        id="control_dam",
        description="Operate the flood control dam",
        trigger_condition=turn_bolt_trigger,
        action=turn_bolt_action,
        required_room="DAM_CONTROL",
        score_reward=15,
        completion_message="The dam machinery rumbles as water levels change!",
        failure_message="Nothing seems to happen."
    )
    
    return Puzzle(
        id="dam_control", 
        name="Flood Control Dam #3",
        description="Master the ancient dam controls",
        steps=[step],
        is_repeatable=True  # Player can toggle dam multiple times
    )


def _create_treasure_collection_puzzle() -> Puzzle:
    """Multi-step treasure gathering puzzle."""
    
    def treasure_taken_trigger(game, command_verb, target_object, **kwargs):
        if command_verb != "take":
            return False
            
        # Check if taking a valuable object
        target_obj = game._find_object(target_object) if target_object else None
        if target_obj:
            return target_obj.get_attribute("treasure", False)
        return False
    
    def treasure_taken_action(game, puzzle_manager, step, **kwargs):
        # Track number of treasures collected
        current_count = puzzle_manager.get_flag("treasures_collected", 0)
        puzzle_manager.set_flag("treasures_collected", current_count + 1)
        
        # Award points based on treasure value
        target_obj = game._find_object(kwargs.get("target_object", ""))
        if target_obj:
            value = target_obj.get_attribute("treasure_value", 10)
            step.score_reward = value
        
        return True
    
    collect_step = PuzzleStep(
        id="collect_treasures",
        description="Collect valuable treasures throughout the game",
        trigger_condition=treasure_taken_trigger,
        action=treasure_taken_action,
        score_reward=0,  # Variable based on treasure
        completion_message="You have collected a valuable treasure!"
    )
    
    return Puzzle(
        id="treasure_hunt",
        name="Treasure Collection",
        description="Gather the scattered treasures of Zork",
        steps=[collect_step],
        is_repeatable=True  # Multiple treasures to collect
    )


# ============================================================================
# GAME ENGINE INTEGRATION
# ============================================================================

def integrate_puzzles_into_game(game_engine):
    """Integrate puzzle system into the main game engine."""
    
    # Create and attach puzzle manager
    game_engine.puzzle_manager = create_authentic_zork_puzzles(game_engine)
    
    # Store original command processor for chaining
    original_process_command = game_engine._process_command
    
    def enhanced_process_command(user_input: str):
        """Enhanced command processor that checks for puzzle triggers."""
        
        # Parse the command
        command = game_engine.parser.parse(user_input)
        
        # Check if this command triggers any puzzles (before normal processing)
        if command:
            triggered, message = game_engine.puzzle_manager.attempt_puzzle_action(
                command_verb=command.verb,
                target_object=command.noun,
                target_room=game_engine.player.current_room,
                user_input=user_input,
                command=command
            )
            
            if triggered and message:
                print(message)
        
        # Continue with normal command processing
        return original_process_command(user_input)
    
    # Replace the command processor
    game_engine._process_command = enhanced_process_command
    
    return game_engine.puzzle_manager