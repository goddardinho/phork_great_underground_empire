"""Main game engine - Coordinates all game systems."""

from typing import Dict, List, Optional, Tuple, Any
import sys
import json
import datetime
import re
import logging
from pathlib import Path
from .world.world import World
from .world.room import Room
from .world.room_loader import ZorkRoomLoader
from .entities.player import Player
from .entities.objects import GameObject
from .entities.object_manager import ObjectManager
from .entities.object_loader import ZorkObjectLoader
from .entities.npc_manager import NPCManager
from .entities.combat import CombatManager
from .parser.command_parser import CommandParser, Command
from .responses import ZorkResponses
from .puzzles import integrate_puzzles_into_game
from .score import ScoreManager
from .combinations import integrate_combinations_into_game


class GameEngine:
    """Main game engine that coordinates all game systems."""
    
    def __init__(self, use_mud_files: bool = False, mud_directory: Optional[Path] = None, debug_mode: bool = False) -> None:
        self.world = World()
        self.player = Player()
        self.parser = CommandParser()
        self.responses = ZorkResponses()
        self.object_manager = ObjectManager()  # Central object registry
        self.npc_manager = NPCManager()  # Central NPC registry
        self.combat_manager = CombatManager()  # Combat and fighting system
        
        # Initialize with some test NPCs
        self._create_initial_npcs()
        self.running = True
        self.debug_mode = debug_mode  # Store debug mode setting
        self.puzzle_manager = None  # Will be initialized after world creation
        self.score_manager = ScoreManager()
        self.combination_manager = None  # Will be initialized after world creation
        
        # Initialize world from .mud files or create a basic test world
        if use_mud_files:
            self._load_world_from_mud_files(mud_directory)
        else:
            self._create_initial_world()
            
        # Initialize puzzle system after world creation
        self.puzzle_manager = integrate_puzzles_into_game(self)
        
        # Initialize object combination system after world creation  
        self.combination_manager = integrate_combinations_into_game(self)
    
    def run(self) -> None:
        """Main game loop."""
        # Add completion message for loading process
        if not self.debug_mode:
            print("Everything is ready. The grue is hungry...\n")
        else:
            print("\n" + "="*50)
            print("DEBUG MODE ENABLED")
            print("="*50)
            print("Extra commands available:")
            print("  debug npc - Test NPC system")
            print("  debug combat - Test combat system")
            print("  debug menu - Show debug menu")
            print("="*50)
        self._show_welcome()
        self._look_around()
        
        while self.running:
            try:
                user_input = input("> ").strip()
                if user_input:
                    self._process_command(user_input)
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
    
    def _process_command(self, user_input: str) -> None:
        """Process a single user command."""
        
        # Check if we're awaiting disambiguation
        if self.player.awaiting_disambiguation:
            self._handle_disambiguation_response(user_input)
            return
        
        command = self.parser.parse(user_input)
        
        if not command:
            print("Beg pardon?")
            return
        
        # Route command to appropriate handler
        self._route_command(command, user_input)
    
    def _route_command(self, command, user_input: str) -> None:
        """Route a command to its appropriate handler (extracted from _process_command)."""
        verb = command.verb
        
        # Commands that don't consume moves
        non_move_commands = ["inventory", "score", "help", "brief", "verbose"]
        
        # Increment move counter for most commands (except info/display commands)
        if verb not in non_move_commands:
            self.score_manager.increment_moves()
        
        if verb in ["north", "south", "east", "west", "northeast", "northwest", 
                   "southeast", "southwest", "up", "down", "in", "out", "enter", "exit"]:
            self._handle_movement(verb)
        elif verb == "go" and command.noun:
            # Handle "go north", "go east", etc.
            direction = command.noun
            if direction in ["north", "south", "east", "west", "northeast", "northwest",
                           "southeast", "southwest", "up", "down", "in", "out", "enter", "exit"]:
                self._handle_movement(direction)
            else:
                print(f"I don't know how to go {direction}.")
        elif verb == "climb":
            # Handle climb command
            self._handle_climb(command)
        elif verb == "look":
            self._handle_look(command)
        elif verb == "examine":
            self._handle_examine(command)
        elif verb == "inventory":
            self._handle_inventory()
        elif verb == "take":
            self._handle_take(command)
        elif verb == "drop":
            self._handle_drop(command)
        elif verb == "open":
            self._handle_open(command)
        elif verb == "close":
            self._handle_close(command)
        elif verb == "read":
            self._handle_read(command)
        elif verb == "put":
            self._handle_put(command)
        elif verb == "get":
            self._handle_get(command)
        elif verb == "q" or verb == "quit":
            self._handle_quit()
        elif verb == "help":
            self._handle_help()
        elif verb == "brief":
            self._handle_brief()
        elif verb == "verbose":
            self._handle_verbose()
        elif verb == "light":
            self._handle_light(command)
        elif verb == "extinguish":
            self._handle_extinguish(command)
        elif verb == "unlock":
            self._handle_unlock(command)
        elif verb == "lock":
            self._handle_lock(command)
        elif verb == "score":
            self._handle_score()
        elif verb == "heat":
            self._handle_heat(command)
        elif verb == "cool":
            self._handle_cool(command) 
        elif verb == "combine":
            self._handle_combine(command)
        elif verb == "break":
            self._handle_break_with(command)
        elif verb == "pour":
            self._handle_pour_on(command)
        elif verb == "apply" or verb == "use":
            self._handle_use_tool(command)
        elif verb == "climb":
            self._handle_climb(command)
        elif verb == "save":
            self._handle_save(command)
        elif verb == "restore" or verb == "load":
            self._handle_restore(command)
        elif verb == "talk":
            self._handle_talk(command)
        elif verb == "ask":
            self._handle_ask(command)
        elif verb == "greet":
            self._handle_greet(command)
        elif verb == "say":
            self._handle_say(command, user_input)
        elif verb == "attack":
            self._handle_attack(command)
        elif verb == "defend":
            self._handle_defend(command)
        elif verb == "flee":
            self._handle_flee(command)
        elif verb == "debug" and self.debug_mode:
            self._handle_debug_command(command)
        else:
            # Check for special Easter egg commands first
            if self.responses.is_special_command(verb):
                print(self.responses.get_special_command_response(verb))
            else:
                print(self.responses.get_unknown_command_response(user_input))
    
    def _handle_movement(self, direction: str) -> None:
        """Handle player movement."""
        current_room = self.world.get_room(self.player.current_room)
        if not current_room:
            print("Error: You are in an unknown location!")
            return
        
        target_room_id = current_room.get_exit(direction)
        if target_room_id:
            target_room = self.world.get_room(target_room_id)
            if target_room:
                # Move player and show room (visited status handled in _look_around)
                self.player.move_to_room(target_room_id)
                self._look_around()
                
                # Check for dangers after moving
                death_message = self._check_danger()
                if death_message:
                    print()
                    print(death_message)
                    print("\n*** You have died ***")
                    print("Would you like to restart, restore a saved game, or quit?")
                    # For now, just end the game
                    self.running = False
            else:
                print("Error: That exit leads nowhere!")
        else:
            print(self.responses.get_cant_go_response())
    
    def _handle_look(self, command: Command) -> None:
        """Handle look command."""
        if command.noun:
            # Looking at specific object - use examine functionality
            self._handle_examine(command)
        else:
            # Looking around the room - always show full description
            self._look_around(force_verbose=True)
    
    def _handle_inventory(self) -> None:
        """Handle inventory command."""
        if not self.player.inventory:
            print("You are empty-handed.")
        else:
            print("You are carrying:")
            for item_id in self.player.inventory:
                obj = self.object_manager.get_object(item_id)
                if obj:
                    print(f"  {obj.name}")
    
    def _handle_take(self, command: Command) -> None:
        """Handle take command."""
        if not command.noun:
            print("Take what?")
            return
        
        # Find the object
        target_obj = self._find_object(command.noun)
        if not target_obj:
            if self.player.awaiting_disambiguation:
                self.player.pending_command = command
                self._show_disambiguation_prompt()
            else:
                print(self.responses.get_dont_see_object_response(command.noun))
            return
        
        # Check if this is a bulk action object (ALL, EVERYTHING, etc.)
        if target_obj.is_bulk_action():
            self._handle_bulk_action("take", target_obj)
            return
        
        if not target_obj.is_takeable():
            print(f"You cannot take that.")
            return
        
        if self.player.is_inventory_full():
            print("Your load is too heavy.")
            return
        
        # Find where the object is located
        location_type, container_id = self._find_object_location(target_obj)
        
        if location_type == "inventory":
            print("You already have that.")
            return
        elif location_type == "room":
            # Take from room
            current_room = self.world.get_room(self.player.current_room)
            if current_room:
                current_room.remove_item(target_obj.id)
                self.player.add_to_inventory(target_obj.id)
                print(f"Taken: {target_obj.name}")
                
                # Award treasure score (OFVAL) if this is a treasure
                points_awarded = self.score_manager.find_treasure(target_obj.id)
                if points_awarded > 0:
                    print(f"(You have found a treasure worth {points_awarded} points!)")
        elif location_type == "container":
            # Take from container
            container = self.object_manager.get_object(container_id) if container_id else None
            if container and container.is_open():
                container.remove_from_container(target_obj.id)
                self.player.add_to_inventory(target_obj.id)
                print(f"Taken: {target_obj.name}")
                
                # Award treasure score (OFVAL) if this is a treasure  
                points_awarded = self.score_manager.find_treasure(target_obj.id)
                if points_awarded > 0:
                    print(f"(You have found a treasure worth {points_awarded} points!)")
            elif container and not container.is_open():
                print(f"The {container.name} is closed.")
            else:
                print(self.responses.get_cant_do_that_response())
        else:
            print(f"I cannot reach that.")
    
    def _handle_drop(self, command: Command) -> None:
        """Handle drop command with bulk action support."""
        if not command.noun:
            print("Drop what?")
            return
        
        target_obj = self._find_object(command.noun, check_inventory_only=True)
        if not target_obj:
            print(f"You don't have a {command.noun}.")
            return
            
        # Check if this is a bulk action object
        if target_obj.is_bulk_action():
            self._handle_bulk_action("drop", target_obj)
            return
        
        # Object is in inventory, drop it
        self.player.remove_from_inventory(target_obj.id)
        current_room = self.world.get_room(self.player.current_room)
        if current_room:
            current_room.add_item(target_obj.id)
        print(f"Dropped: {target_obj.name}")
    
    def _handle_drop(self, command: Command) -> None:
        """Handle drop command."""
        if not command.noun:
            print("Drop what?")
            return
        
        # Find object - this will handle disambiguation if needed
        target_obj = self._find_object(command.noun, check_inventory_only=True)
        
        # If disambiguation is in progress, save command for later execution
        if self.player.awaiting_disambiguation:
            self.player.pending_command = command
            self._show_disambiguation_prompt()
            return
        
        if not target_obj:
            print(self.responses.get_dont_see_object_response(command.noun))
            return
        
        # Check if object is in inventory
        if target_obj.id not in self.player.inventory:
            print(self.responses.get_inventory_response("dont_have"))
            return
        
        current_room = self.world.get_room(self.player.current_room)
        if current_room:
            self.player.remove_from_inventory(target_obj.id)
            current_room.add_item(target_obj.id)
            print(f"Dropped: {target_obj.name}")
    
    def _handle_examine(self, command: Command) -> None:
        """Handle examine command for detailed object inspection."""
        if not command.noun:
            print("Examine what?")
            return
        
        target_obj = self._find_object(command.noun)
        if not target_obj:
            if self.player.awaiting_disambiguation:
                self.player.pending_command = command
                self._show_disambiguation_prompt()
            else:
                print(self.responses.get_dont_see_object_response(command.noun))
            return
        
        # Determine object location for context-appropriate description
        location_type, container_id = self._find_object_location(target_obj)
        
        # Show base description with dynamic updates
        description = target_obj.description
        
        # Special handling for different object types
        if target_obj.id == "WINDOW":
            if target_obj.is_open():
                description = "A small window in the corner of the house. It is open, letting in fresh air."
            else:
                description = "A small window in the corner of the house. It is closed tightly."
        elif target_obj.is_container():
            # For containers, always focus on container state/contents regardless of location
            # "look in X" should be about the container, not its room description
            contents = target_obj.get_contents()
            
            if target_obj.is_open():
                description = f"The {target_obj.name} is open."
            else:
                description = f"The {target_obj.name} is closed."
                if contents:
                    description += " There appears to be something inside."
        
        print(description)
        
        # Show container contents if it's an open container
        if target_obj.is_container() and target_obj.is_open():
            contents = target_obj.get_contents()
            if contents:
                print("It contains:")
                for item_id in contents:
                    item = self.object_manager.get_object(item_id)
                    if item:
                        print(f"  {item.name}")
            else:
                print("It is empty.")
    
    def _handle_climb(self, command: Command) -> None:
        """Handle climb command - context-dependent movement."""
        if not command.noun:
            print("Climb what?")
            return
        
        current_room = self.world.get_room(self.player.current_room)
        if not current_room:
            print("Error: You are in an unknown location!")
            return
        
        # Normalize potential climb targets
        climb_target = command.noun.lower().strip()
        
        # Check for tree climbing in forest room
        if climb_target in ["tree", "large tree", "big tree", "trees"]:
            # Check if we're in a room with a tree we can climb
            room_desc = current_room.description.lower()
            if "tree" in room_desc and "up" in current_room.exits:
                # This room has a tree and an up exit - climb the tree!
                print("You climb up the tree.")
                self._handle_movement("up")
                return
            else:
                print("There's nothing here you can climb.")
                return
        
        # Check for ladder climbing
        elif climb_target in ["ladder", "stairs", "steps", "staircase", "stairway"]:
            if "up" in current_room.exits:
                print(f"You climb up the {climb_target}.")
                self._handle_movement("up") 
                return
            elif "down" in current_room.exits:
                print(f"You climb down the {climb_target}.")
                self._handle_movement("down")
                return
            else:
                print(f"There's no {climb_target} here to climb.")
                return
        
        # Check for rope climbing (if rope is present)
        elif climb_target in ["rope", "cord", "line"]:
            # Look for rope in room or inventory
            rope_obj = None
            for obj_id in self.player.inventory + current_room.items:
                obj = self.object_manager.get_object(obj_id)
                if obj and obj.matches("rope"):
                    rope_obj = obj
                    break
            
            if rope_obj:
                if "up" in current_room.exits:
                    print("You climb up the rope.")
                    self._handle_movement("up")
                    return
                elif "down" in current_room.exits:
                    print("You climb down the rope.")
                    self._handle_movement("down") 
                    return
                else:
                    print("The rope doesn't lead anywhere useful.")
                    return
            else:
                print("I don't see any rope here to climb.")
                return
        
        # Generic climbing - check if there's an "up" direction 
        elif "up" in current_room.exits:
            print(f"You can't climb the {climb_target}.")
            return
        else:
            print("There's nothing here you can climb.")
    
    def _handle_open(self, command: Command) -> None:
        """Handle open command with enhanced container support."""
        if not command.noun:
            print(self.responses.get_cant_do_that_response())
            return
        
        target_obj = self._find_object(command.noun)
        if not target_obj:
            print(self.responses.get_dont_see_object_response(command.noun))
            return
        
        # Check if object can be opened
        if not target_obj.is_openable():
            print(self.responses.get_action_response("cant_open", target_obj.name))
            return
            
        # Check if already open
        if target_obj.is_open():
            print(self.responses.get_action_response("already_open", target_obj.name))
            return
            
        # Check if locked
        if target_obj.is_locked():
            print(f"The {target_obj.name} is locked.")
            return
        
        # Open the object
        target_obj.set_attribute("open", True)
        
        # Custom messages for different object types
        if target_obj.id == "WINDOW":
            print(f"You open the {target_obj.name} wider. Fresh air flows in.")
        elif target_obj.id == "MAILBOX":
            print(f"You open the {target_obj.name}.")
        else:
            print(f"Opened.")
        
        # Show contents if it's a container
        if target_obj.is_container():
            contents = target_obj.get_contents()
            if contents:
                print("Inside you find:")
                for item_id in contents:
                    item = self.object_manager.get_object(item_id)
                    if item:
                        print(f"  {item.name}")
            else:
                print("It is empty.")
    
    def _handle_close(self, command: Command) -> None:
        """Handle close command with enhanced container support."""
        if not command.noun:
            print(self.responses.get_cant_do_that_response())
            return
        
        target_obj = self._find_object(command.noun)
        if not target_obj:
            print(self.responses.get_dont_see_object_response(command.noun))
            return
        
        # Check if object can be closed
        if not target_obj.is_openable():
            print(self.responses.get_action_response("cant_close", target_obj.name))
            return
        
        # Check if already closed
        if not target_obj.is_open():
            print(self.responses.get_action_response("already_closed", target_obj.name))
            return
        
        # Close the object
        target_obj.set_attribute("open", False)
        
        # Custom messages for different object types
        if target_obj.id == "WINDOW":
            print(f"You close the {target_obj.name} tightly, shutting out the fresh air.")
        elif target_obj.id == "MAILBOX":
            print(f"You close the {target_obj.name}.")
        else:
            print(f"Closed.")
    
    def _handle_read(self, command: Command) -> None:
        """Handle read command."""
        if not command.noun:
            print("Read what?")
            return
        
        target_obj = self._find_object(command.noun)
        if not target_obj:
            print(f"I don't see a {command.noun} here.")
            return
        
        # Check if object has readable content
        readable_text = target_obj.get_attribute("readable_text", None)
        if readable_text:
            print(readable_text)
        elif target_obj.get_attribute("readable", False):
            print(f"The {target_obj.name} has no text on it.")
        else:
            print(f"How can I read a {target_obj.name}?")

    def _handle_put(self, command: Command) -> None:
        """Handle put command (put X in Y) with enhanced container support."""
        if not command.noun:
            print("Put what?")
            return
        
        if not command.preposition or command.preposition != "in":
            print("Put it in what?")
            return
        
        if not command.noun2:
            print("Put it in what?")
            return
        
        # Find the item to put
        item_obj = self._find_object(command.noun)
        if not item_obj:
            print(self.responses.get_dont_see_object_response(command.noun))
            return
        
        # Find the container
        container_obj = self._find_object(command.noun2)
        if not container_obj:
            print(self.responses.get_dont_see_object_response(command.noun2))
            return
        
        # Check if target is a container
        if not container_obj.is_container():
            print(self.responses.get_action_response("not_container", container_obj.name))
            return
        
        # Check if container is openable and open
        if container_obj.is_openable() and not container_obj.is_open():
            print(f"The {container_obj.name} is closed.")
            return
            
        # Check if container is at capacity
        if container_obj.is_at_capacity():
            print(f"The {container_obj.name} is full.")
            return
        
        # Make sure the item isn't the container itself
        if item_obj.id == container_obj.id:
            print("That would be quite a contortion!")
            return
        
        # Find where the item currently is
        location_type, current_container_id = self._find_object_location(item_obj)
        
        if location_type == "inventory":
            # Remove from inventory and add to container
            self.player.remove_from_inventory(item_obj.id)
            container_obj.add_to_container(item_obj.id)
            print(f"You put the {item_obj.name} in the {container_obj.name}.")
        elif location_type == "room":
            # Remove from room and add to container
            current_room = self.world.get_room(self.player.current_room)
            if current_room:
                current_room.remove_item(item_obj.id)
                container_obj.add_to_container(item_obj.id)
                print(f"You put the {item_obj.name} in the {container_obj.name}.")
        elif location_type == "container":
            # Move from one container to another
            current_container = self.object_manager.get_object(current_container_id) if current_container_id else None
            if current_container:
                current_container.remove_from_container(item_obj.id)
                container_obj.add_to_container(item_obj.id)
                print(f"You put the {item_obj.name} in the {container_obj.name}.")
        else:
            print(f"You can't reach the {item_obj.name}.")

    def _handle_get(self, command: Command) -> None:
        """Handle get command (get X from Y or just get X) with enhanced container support."""
        if not command.noun:
            print("Get what?")
            return
        
        # Check for "get X from Y" syntax
        if command.preposition == "from" and command.noun2:
            # Find the container
            container_obj = self._find_object(command.noun2)
            if not container_obj:
                print(self.responses.get_dont_see_object_response(command.noun2))
                return
            
            if not container_obj.is_container():
                print(self.responses.get_action_response("not_container", container_obj.name))
                return
            
            # Check if container is openable and open
            if container_obj.is_openable() and not container_obj.is_open():
                print(f"The {container_obj.name} is closed.")
                return
                
            # Check if container is empty
            if not container_obj.get_contents():
                print(self.responses.get_action_response("nothing_inside", container_obj.name))
                return
            
            # Find the item in the container - use disambiguation
            # Temporarily switch scope to just this container for finding
            container_items = []
            for item_id in container_obj.get_contents():
                obj = self.object_manager.get_object(item_id)
                if obj and obj.matches(command.noun):
                    container_items.append(obj)
            
            if not container_items:
                print(f"I don't see a {command.noun} in the {container_obj.name}.")
                return
            elif len(container_items) == 1:
                item_obj = container_items[0]
            else:
                # Multiple matches in container - show disambiguation
                self.player.awaiting_disambiguation = True
                self.player.disambiguation_options = container_items
                self.player.pending_command = command
                print(f"Which {command.noun} do you mean:")
                for i, obj in enumerate(container_items, 1):
                    location_desc = f"in the {container_obj.name}"
                    print(f"  {i}. The {obj.name} ({location_desc})")
                return
            
            # Remove from container and add to inventory
            container_obj.remove_from_container(item_obj.id)
            self.player.add_to_inventory(item_obj.id)
            print(f"You take the {item_obj.name} from the {container_obj.name}.")
        else:
            # Regular get command (equivalent to take)
            self._handle_take(command)
    
    def _find_object(self, noun: str, check_inventory_only: bool = False) -> Optional['GameObject']:
        """Find an object by name or alias. Handles disambiguation if multiple matches found."""
        matches = self._find_all_objects(noun, check_inventory_only)
        
        if not matches:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            # Multiple matches - initiate disambiguation
            self.player.awaiting_disambiguation = True
            self.player.disambiguation_options = matches
            self.player.pending_command = None  # Will be set by caller if needed
            return None  # Signal ambiguity
    
    def _find_object_location(self, obj: 'GameObject') -> Tuple[str, Optional[str]]:
        """Find where an object is located. Returns (location_type, container_id)."""
        current_room = self.world.get_room(self.player.current_room)
        
        # Check if in current room
        if current_room and obj.id in current_room.items:
            return ("room", None)
        
        # Check if in inventory
        if obj.id in self.player.inventory:
            return ("inventory", None)
        
        # Check if in containers in current room
        if current_room:
            for item_id in current_room.items:
                container = self.object_manager.get_object(item_id)
                if container and container.is_container() and obj.id in container.get_contents():
                    return ("container", container.id)
        
        # Check if in containers in inventory
        for item_id in self.player.inventory:
            container = self.object_manager.get_object(item_id)
            if container and container.is_container() and obj.id in container.get_contents():
                return ("container", container.id)
        
        return ("unknown", None)
    
    def _handle_quit(self) -> None:
        """Handle quit command."""
        print("Are you sure you want to quit? (y/n)")
        response = input("> ").strip().lower()
        if response.startswith('y'):
            print("Thanks for playing!")
            self.running = False
    
    def _handle_help(self) -> None:
        """Handle help command."""
        help_text = """
Available commands:
  Movement: north, south, east, west, up, down (or n, s, e, w, u, d)
  Actions: look, examine <object>, take <object>, drop <object>, inventory (or i)
  Object Interaction: open <object>, close <object>, read <object>
  Container Operations: put <object> in <container>, get <object> from <container>
  Light Sources: light <object>, extinguish <object>
  Object Combinations: heat <object>, cool <object>, combine <object> <object>
  Tool Usage: break <object> with <tool>, use <tool> on <object>, apply <tool>
  Game Management: save [filename], restore [filename], score
  Display: brief (short room descriptions), verbose (full room descriptions)
  Other: help, quit (or q)

Shortcuts are available for most commands.
Use 'restore' without a filename to see available saves.
"""
        print(help_text)
    
    def _handle_brief(self) -> None:
        """Handle brief command - enable brief room descriptions."""
        self.player.brief_mode = True
        print("Brief descriptions enabled. Visited rooms will show short descriptions.")
    
    def _handle_verbose(self) -> None:
        """Handle verbose command - enable full room descriptions."""
        self.player.brief_mode = False
        print("Verbose descriptions enabled. All rooms will show full descriptions.")
    
    def _handle_light(self, command: Command) -> None:
        """Handle lighting objects like torches."""
        if not command.noun:
            print("Light what?")
            return
        
        obj = self._find_object(command.noun)
        if not obj:
            print(f"I don't see a {command.noun} here.")
            return
        
        if not obj.is_light_source():
            print(f"You can't light the {obj.name}.")
            return
        
        if obj.is_lit():
            print(f"The {obj.name} is already lit.")
            return
        
        # Check if player has matches or other lighting source
        has_matches = False
        for item_id in self.player.inventory:
            match_obj = self.object_manager.get_object(item_id)
            if match_obj and "matches" in match_obj.name.lower():
                uses = match_obj.get_attribute("uses_remaining", 0)
                if uses > 0:
                    match_obj.set_attribute("uses_remaining", uses - 1)
                    has_matches = True
                    break
        
        if not has_matches:
            print("You have no way to light it.")
            return
        
        # Light the object
        obj.set_attribute("lit", True)
        print(f"The {obj.name} is now lit.")
    
    def _handle_extinguish(self, command: Command) -> None:
        """Handle extinguishing light sources."""
        if not command.noun:
            print("Extinguish what?")
            return
        
        obj = self._find_object(command.noun)
        if not obj:
            print(f"I don't see a {command.noun} here.")
            return
        
        if not obj.is_light_source():
            print(f"The {obj.name} is not a light source.")
            return
        
        if not obj.is_lit():
            print(f"The {obj.name} is not lit.")
            return
        
        obj.set_attribute("lit", False)
        print(f"The {obj.name} is extinguished.")

    def _handle_unlock(self, command: Command) -> None:
        """Handle unlock command for doors, containers, etc."""
        if not command.noun:
            print("Unlock what?")
            return
        
        # Check if we're unlocking a grate (special puzzle object)
        if command.noun.lower() == "grate":
            current_room = self.world.get_room(self.player.current_room)
            if current_room and current_room.id == "GRATE_ROOM":
                # Check if player has keys
                if "KEYS" in self.player.inventory:
                    # This will be handled by the puzzle system
                    print("You unlock the grate with the rusty keys.")
                    # Add the downward exit
                    current_room.exits["down"] = "CAVE"
                    return
                else:
                    print("You don't have anything to unlock it with.")
                    return
            else:
                print("I don't see a grate here.")
                return
        
        # Find the object to unlock
        obj = self._find_object(command.noun)
        if not obj:
            print(f"I don't see a {command.noun} here.")
            return
        
        # Check if object can be unlocked
        if not obj.is_openable():
            print(f"You can't unlock the {obj.name}.")
            return
            
        if not obj.is_locked():
            print(f"The {obj.name} isn't locked.")
            return
        
        # Simple unlock (would need key checking in full implementation)
        obj.set_attribute("locked", False)
        print(f"You unlock the {obj.name}.")
        
    def _handle_lock(self, command: Command) -> None:
        """Handle lock command for doors, containers, etc."""
        if not command.noun:
            print("Lock what?")
            return
        
        obj = self._find_object(command.noun)
        if not obj:
            print(f"I don't see a {command.noun} here.")
            return
        
        # Check if object can be locked
        if not obj.is_openable():
            print(f"You can't lock the {obj.name}.")
            return
            
        if obj.is_locked():
            print(f"The {obj.name} is already locked.")
            return
            
        if obj.is_open():
            print(f"You can't lock the {obj.name} while it's open.")
            return
        
        # Simple lock (would need key checking in full implementation)
        obj.set_attribute("locked", True)
        print(f"You lock the {obj.name}.")
    
    def _handle_score(self) -> None:
        """Handle score command - display current score and ranking."""
        # Display canonical score report (moves already tracked in _route_command)
        print(self.score_manager.get_score_report())
    
    def _handle_heat(self, command: Command) -> None:
        """Handle heat command for object transformations."""
        if not command.noun:
            print("Heat what?")
            return
            
        primary_obj = self._find_object(command.noun)
        if not primary_obj:
            print(f"I don't see a {command.noun} here.")
            return
            
        # Look for heat source in inventory or room
        heat_source = None
        for item_id in self.player.inventory:
            obj = self.object_manager.get_object(item_id)
            if obj and obj.is_lit():  # Lit objects can provide heat
                heat_source = obj
                break
        
        if not heat_source:
            print("You need a heat source.")
            return
            
        # Attempt interaction
        success, message, result_obj = self.combination_manager.perform_interaction(
            primary_obj.id, heat_source.id, "heat", self.player.current_room, self.object_manager
        )
        
        print(message)
        
        if success and result_obj:
            # Handle object transformation
            self._handle_object_transformation(primary_obj.id, result_obj)
    
    def _handle_cool(self, command: Command) -> None:
        """Handle cool command for object transformations.""" 
        if not command.noun:
            print("Cool what?")
            return
            
        primary_obj = self._find_object(command.noun)
        if not primary_obj:
            print(f"I don't see a {command.noun} here.")
            return
            
        # For cooling, we might need water or cold conditions
        print("You need something cold to cool it with.")
    
    def _handle_combine(self, command: Command) -> None:
        """Handle combine command for object combinations."""
        if not command.noun or not command.noun2:
            print("Combine what with what?")
            return
            
        obj1 = self._find_object(command.noun)
        obj2 = self._find_object(command.noun2)
        
        if not obj1 or not obj2:
            print("I can't find those objects.")
            return
            
        # Attempt combination
        success, message, result_obj = self.combination_manager.perform_interaction(
            obj1.id, obj2.id, "combine", self.player.current_room, self.object_manager
        )
        
        print(message)
        
        if success and result_obj:
            self._handle_object_combination(obj1.id, obj2.id, result_obj)
    
    def _handle_break_with(self, command: Command) -> None:
        """Handle break X with Y command."""
        if not command.noun or not command.noun2:
            print("Break what with what?") 
            return
            
        target_obj = self._find_object(command.noun)
        tool_obj = self._find_object(command.noun2)
        
        if not target_obj or not tool_obj:
            print("I can't find those objects.")
            return
            
        # Attempt breaking
        success, message, result_obj = self.combination_manager.perform_interaction(
            target_obj.id, tool_obj.id, "break", self.player.current_room, self.object_manager
        )
        
        print(message)
        
        if success and result_obj:
            self._handle_object_transformation(target_obj.id, result_obj)
    
    def _handle_pour_on(self, command: Command) -> None:
        """Handle pour X on Y command."""
        if not command.noun or not command.noun2:
            print("Pour what on what?")
            return
            
        liquid_obj = self._find_object(command.noun)
        target_obj = self._find_object(command.noun2)
        
        if not liquid_obj or not target_obj:
            print("I can't find those objects.")
            return
            
        # Attempt pouring
        success, message, result_obj = self.combination_manager.perform_interaction(
            target_obj.id, liquid_obj.id, "pour", self.player.current_room, self.object_manager
        )
        
        print(message)
    
    def _handle_use_tool(self, command: Command) -> None:
        """Handle use/apply X on Y command."""
        if not command.noun or not command.noun2:
            print("Use what on what?")
            return
            
        tool_obj = self._find_object(command.noun)  
        target_obj = self._find_object(command.noun2)
        
        if not tool_obj or not target_obj:
            print("I can't find those objects.")
            return
            
        # Attempt tool usage
        success, message, result_obj = self.combination_manager.perform_interaction(
            target_obj.id, tool_obj.id, "use", self.player.current_room, self.object_manager
        )
        
        print(message)
    
    def _handle_object_transformation(self, original_id: str, new_id: str) -> None:
        """Handle when an object transforms into another object."""
        # Remove original object from game
        original_obj = self.object_manager.get_object(original_id)
        if not original_obj:
            return
            
        # Find where original object was located
        location_type, container_id = self._find_object_location(original_obj)
        
        # Remove from current location
        if location_type == "inventory":
            self.player.remove_from_inventory(original_id)
        elif location_type == "room":
            current_room = self.world.get_room(self.player.current_room)
            if current_room:
                current_room.remove_item(original_id)
        elif location_type == "container" and container_id:
            container = self.object_manager.get_object(container_id)
            if container:
                container.remove_from_container(original_id)
        
        # Create and place new object (this would need the new object definition)
        # For now, just update the ID mapping
        if new_id in self.object_manager.objects:
            new_obj = self.object_manager.get_object(new_id)
            
            # Place in same location as original
            if location_type == "inventory":
                self.player.add_to_inventory(new_id)
            elif location_type == "room":
                current_room = self.world.get_room(self.player.current_room)
                if current_room:
                    current_room.add_item(new_id)
            elif location_type == "container" and container_id:
                container = self.object_manager.get_object(container_id)
                if container:
                    container.add_to_container(new_id)
    
    def _handle_object_combination(self, obj1_id: str, obj2_id: str, result_id: str) -> None:
        """Handle when two objects are combined to create a new object."""
        # Remove both original objects
        self._remove_object_from_game(obj1_id)
        self._remove_object_from_game(obj2_id)
        
        # Add result object to inventory (most logical place for combined objects)
        if result_id in self.object_manager.objects:
            self.player.add_to_inventory(result_id)
    
    def _remove_object_from_game(self, obj_id: str) -> None:
        """Remove an object from wherever it is in the game."""
        obj = self.object_manager.get_object(obj_id)
        if not obj:
            return
            
        location_type, container_id = self._find_object_location(obj)
        
        if location_type == "inventory":
            self.player.remove_from_inventory(obj_id)
        elif location_type == "room":
            current_room = self.world.get_room(self.player.current_room)
            if current_room:
                current_room.remove_item(obj_id)
        elif location_type == "container" and container_id:
            container = self.object_manager.get_object(container_id)
            if container:
                container.remove_from_container(obj_id)
    
    def _find_all_objects(self, noun: str, check_inventory_only: bool = False) -> List['GameObject']:
        """Find all objects matching the given noun in accessible locations."""
        matches = []
        
        # Always check bulk action objects first (they're globally available)
        for obj_id, obj in self.object_manager.objects.items():
            if obj.is_bulk_action() and obj.matches(noun):
                matches.append(obj)
        
        if check_inventory_only:
            # Only check inventory (for drop command)
            for item_id in self.player.inventory:
                obj = self.object_manager.get_object(item_id)
                if obj and obj.matches(noun) and not obj.is_bulk_action():
                    matches.append(obj)
        else:
            # Check accessible locations
            current_room = self.world.get_room(self.player.current_room)
            
            # Check current room
            if current_room:
                for item_id in current_room.items:
                    obj = self.object_manager.get_object(item_id)
                    if obj and obj.matches(noun) and not obj.is_bulk_action():
                        matches.append(obj)
                        
                    # Also check inside open containers in the room
                    if obj and obj.is_container() and obj.is_open():
                        for contained_id in obj.get_contents():
                            contained_obj = self.object_manager.get_object(contained_id)
                            if contained_obj and contained_obj.matches(noun):
                                matches.append(contained_obj)
            
            # Check inventory  
            for item_id in self.player.inventory:
                obj = self.object_manager.get_object(item_id)
                if obj and obj.matches(noun) and not obj.is_bulk_action():
                    matches.append(obj)
                
                # Also check inside open containers in inventory
                if obj and obj.is_container() and obj.is_open():
                    for contained_id in obj.get_contents():
                        contained_obj = self.object_manager.get_object(contained_id)
                        if contained_obj and contained_obj.matches(noun):
                            matches.append(contained_obj)
        
        return matches
    
    def _handle_disambiguation_response(self, user_input: str) -> None:
        """Handle player's response to disambiguation prompt."""
        user_input = user_input.strip().lower()
        
        # Check for cancel/quit disambiguation
        if user_input in ['cancel', 'quit', 'nevermind', 'none']:
            self._clear_disambiguation()
            print("Cancelled.")
            return
        
        # Try to parse as a number (1, 2, 3, etc.)
        try:
            choice_num = int(user_input)
            if 1 <= choice_num <= len(self.player.disambiguation_options):
                chosen_obj = self.player.disambiguation_options[choice_num - 1]
                self._execute_disambiguated_command(chosen_obj)
                return
            else:
                print(f"Please choose a number between 1 and {len(self.player.disambiguation_options)}.")
                return
        except ValueError:
            pass
        
        # Try to match the response against object descriptions
        for i, obj in enumerate(self.player.disambiguation_options):
            # Check if user input matches part of the object description
            if (user_input in obj.name.lower() or 
                user_input in obj.description.lower() or
                any(user_input in alias.lower() for alias in obj.aliases)):
                self._execute_disambiguated_command(obj)
                return
        
        # No match found
        print("I don't understand. Please choose a number or be more specific.")
        self._show_disambiguation_prompt()
    
    def _execute_disambiguated_command(self, chosen_obj: 'GameObject') -> None:
        """Execute the pending command with the chosen object."""
        if not self.player.pending_command:
            self._clear_disambiguation()
            return
        
        command = self.player.pending_command
        
        # Special handling for "get X from Y" commands that use container-specific disambiguation
        if (command.verb == "get" and command.preposition == "from" and command.noun2):
            # For container disambiguation, directly execute the get operation
            container_obj = self._find_object(command.noun2)
            if container_obj and container_obj.is_container():
                # Check if player can carry it
                if self.player.is_inventory_full():
                    print("Your load is too heavy.")
                else:
                    # Remove from container and add to inventory
                    container_obj.remove_from_container(chosen_obj.id)
                    self.player.add_to_inventory(chosen_obj.id)
                    print(f"You take the {chosen_obj.name} from the {container_obj.name}.")
            self._clear_disambiguation()
            return
        
        # For regular commands, use the mock approach
        original_find_object = self._find_object
        
        def mock_find_object(noun: str) -> Optional['GameObject']:
            # Return the chosen object if the noun matches
            if chosen_obj.matches(noun):
                return chosen_obj
            return original_find_object(noun)
        
        # Temporarily replace the find_object method
        self._find_object = mock_find_object
        
        try:
            # Clear disambiguation state first
            self._clear_disambiguation()
            
            # Re-execute the original command with the chosen object
            self._route_command(command)
        finally:
            # Restore original method
            self._find_object = original_find_object
    
    def _clear_disambiguation(self) -> None:
        """Clear disambiguation state."""
        self.player.awaiting_disambiguation = False
        self.player.disambiguation_options = []
        self.player.pending_command = None
    
    def _show_disambiguation_prompt(self) -> None:
        """Show the disambiguation options to the player."""
        print("Which one do you mean?")
        for i, obj in enumerate(self.player.disambiguation_options, 1):
            location_desc = self._get_object_location_description(obj)
            print(f"  {i}. the {obj.name} ({location_desc})")
        print("(Enter a number, or type 'cancel' to abort)")
    
    def _get_object_location_description(self, obj: 'GameObject') -> str:
        """Get a description of where an object is located."""
        location_type, container_id = self._find_object_location(obj)
        
        if location_type == "inventory":
            return "in your inventory"
        elif location_type == "room":
            return "here"
        elif location_type == "container" and container_id:
            container = self.object_manager.get_object(container_id)
            if container:
                return f"in the {container.name}"
        
        return "somewhere nearby"
    
    def _has_light_source(self) -> bool:
        """Check if player has any active light source."""
        # Check inventory for lit light sources
        for item_id in self.player.inventory:
            obj = self.object_manager.get_object(item_id)
            if obj and obj.is_lit():
                return True
        
        # Check current room for lit light sources
        current_room = self.world.get_room(self.player.current_room)
        if current_room:
            for item_id in current_room.items:
                obj = self.object_manager.get_object(item_id)
                if obj and obj.is_lit():
                    return True
        
        return False
    
    def _check_darkness(self) -> bool:
        """Check if current room is dark and player has no light. Returns True if too dark to see."""
        current_room = self.world.get_room(self.player.current_room)
        if not current_room or not current_room.has_flag("dark"):
            return False
        
        return not self._has_light_source()
    
    def _check_danger(self) -> Optional[str]:
        """Check for room dangers and return death message if applicable."""
        current_room = self.world.get_room(self.player.current_room)
        if not current_room:
            return None
        
        # Check for grue in dark rooms
        if current_room.has_flag("dark") and self._check_darkness():
            import random
            if random.random() < 0.1:  # 10% chance per turn in darkness
                return "You are likely to be eaten by a grue."
        
        # Check for explicitly dangerous/deadly rooms
        if current_room.has_flag("dangerous") or current_room.has_flag("deadly"):
            import random
            if random.random() < 0.05:  # 5% chance per turn in dangerous areas
                return "You have died from the treacherous conditions here."
        
        return None
    
    def _get_atmospheric_description(self) -> Optional[str]:
        """Get additional atmospheric text based on room flags."""
        current_room = self.world.get_room(self.player.current_room)
        if not current_room:
            return None
        
        atmospheric_text = []
        
        if current_room.has_flag("noisy"):
            atmospheric_text.append("Your footsteps echo loudly here.")
        
        if current_room.has_flag("sacred"):
            atmospheric_text.append("An aura of ancient power fills this place.")
        
        if current_room.has_flag("outdoor"):
            atmospheric_text.append("A gentle breeze stirs the air.")
        
        if current_room.has_flag("cold"):
            atmospheric_text.append("The air is frigid here.")
        
        return " ".join(atmospheric_text) if atmospheric_text else None
    
    def _look_around(self, force_verbose: bool = False) -> None:
        """Show the current room description."""
        current_room = self.world.get_room(self.player.current_room)
        if not current_room:
            print("You are in a void.")
            return
        
        # Check for darkness first
        if self._check_darkness():
            print("It is pitch black. You are likely to be eaten by a grue.")
            current_room.visited = True  # Still mark as visited
            return
        
        # Determine how to show the description
        if force_verbose:
            # "look" command - always show full description without room name
            print(current_room.get_description(force_verbose=True, include_name=False))
        elif not current_room.visited:
            # First visit - always show full description regardless of brief mode, without room name
            print(current_room.get_description(force_verbose=True, include_name=False))
        else:
            # Subsequent visit - respect brief mode setting, without room name
            print(current_room.get_description(force_brief=self.player.brief_mode, include_name=False))
        
        # Mark room as visited after showing description
        current_room.visited = True
        
        # Show items in room
        items_here = []
        for item_id in current_room.items:
            obj = self.object_manager.get_object(item_id)
            if obj:
                items_here.append(obj.name)
        
        if items_here:
            if len(items_here) == 1:
                print(f"There is a {items_here[0]} here.")
            else:
                print(f"There are {', '.join(items_here)} here.")
        
        # Show NPCs in room
        npcs_here = self.npc_manager.get_npcs_in_room(current_room.id)
        if npcs_here:
            for npc in npcs_here:
                print(npc.description)
        
        # Show available exits
        if current_room.exits:
            exit_list = list(current_room.exits.keys())
            print(f"Obvious exits: {', '.join(exit_list)}")
        
        # Show atmospheric descriptions based on room flags
        atmospheric = self._get_atmospheric_description()
        if atmospheric:
            print(atmospheric)
    
    def _show_welcome(self) -> None:
        """Show the welcome message."""
        if self.debug_mode:
            welcome_text = """
ZORK I: The Great Underground Empire
A clean Python implementation

Type 'help' for a list of commands.
"""
        else:
            # Canonical Zork introduction - minimal and true to original
            welcome_text = """ZORK I: The Great Underground Empire
Copyright (c) 1981, 1982, 1983 Infocom, Inc. All rights reserved.
ZORK is a registered trademark of Infocom, Inc.
Revision 88 / Serial number 840726

"""
        print(welcome_text)
    
    def _load_world_from_mud_files(self, mud_directory: Optional[Path] = None) -> None:
        """Load world from original Zork .mud files."""
        if mud_directory is None:
            mud_directory = Path("zork_mtl_source")
        
        if not mud_directory.exists():
            if self.debug_mode:
                print(f"Warning: {mud_directory} not found. Creating simple test world instead.")
            else:
                print("Hmm, the original scrolls seem to be missing. Conjuring a basic world...")
            self._create_initial_world()
            return
        
        if self.debug_mode:
            print(f"Loading Zork world from {mud_directory}...")
        else:
            print("The Implementers are consulting the ancient scrolls...")
        
        # Load rooms from .mud files
        room_loader = ZorkRoomLoader(self.world, debug_mode=self.debug_mode)
        room_count = room_loader.load_from_mud_files(mud_directory)
        
        if room_count == 0:
            if self.debug_mode:
                print("Failed to load rooms from .mud files. Creating simple test world instead.")
            else:
                print("The scrolls are written in an ancient tongue. Improvising...")
            self._create_initial_world()
            return
        
        if not self.debug_mode:
            print("The maze of twisty passages is taking shape...")
            
        if self.debug_mode:
            print(f"✓ Loaded {room_count} rooms from original Zork")
        
        # Load objects using new object loader
        object_loader = ZorkObjectLoader(self.object_manager, self.world, debug_mode=self.debug_mode)
        object_count = object_loader.load_from_mud_files(mud_directory)
        
        if not self.debug_mode:
            print("Scattering treasures and hiding rusty swords...")
            
        if self.debug_mode:
            print(f"✓ Loaded {object_count} objects from canonical definitions")
        
        # Set starting room to West of House (just like original Zork)
        starting_room = "WHOUS"
        if starting_room not in self.world.rooms:
            if self.debug_mode:
                print("Warning: Starting room WHOUS not found. Using first available room.")
            starting_room = list(self.world.rooms.keys())[0] if self.world.rooms else "UNKNOWN"
        
        self.player.current_room = starting_room
        
        # Add a subtle completion hint for non-debug mode
        if not self.debug_mode:
            print("Ready to explore the Great Underground Empire!")
    
    def _load_objects_from_mud_files(self, mud_directory: Path) -> None:
        """Load and create objects from .mud files and place them in rooms."""
        
        # Create essential objects that rooms reference
        self._create_mud_objects()
        
        # Process GET-OBJ references in each room and place objects accordingly
        objects_placed = 0
        for room_id, room in self.world.rooms.items():
            # Get the original room data from parser to access object list
            loader = ZorkRoomLoader(self.world)
            parser = loader.parser
            
            # Re-parse to get object references for this room
            for mud_file in mud_directory.glob("*.mud"):
                try:
                    content = mud_file.read_text()
                    # Find this room's definition
                    room_match = re.search(rf'<ROOM\s+"{room_id}"[^>]*>(.*?)(?=<ROOM|$)', content, re.DOTALL)
                    if room_match:
                        room_content = room_match.group(1)
                        # Extract GET-OBJ references
                        obj_refs = re.findall(r'<GET-OBJ\s+"([^"]+)">', room_content)
                        for obj_id in obj_refs:
                            if obj_id in self.object_manager.objects:
                                room.add_item(obj_id)
                                objects_placed += 1
                except Exception as e:
                        logging.warning(f"Failed to process object file: {type(e).__name__}")
                        continue  # Continue if file can't be processed
    
    # These methods are now replaced by the ObjectManager and ZorkObjectLoader system
    # The old object creation code has been removed and replaced with modular architecture
    # Old object creation methods removed - now using ObjectManager and ZorkObjectLoader
    
    def _create_bulk_action_objects(self) -> None:
        """Create canonical Zork bulk action objects (ALL, EVERYTHING, VALUABLES, etc.)."""
        # "ALL" or "EVERYTHING" - takes all visible, takeable items
        all_object = GameObject(
            id="ALL",
            name="everything",
            description="A special command to act on multiple objects at once.",
            aliases=["all", "everything"],
            attributes={
                "bulk_action": True,
                "bulk_type": "all",
                "takeable": True,  # So parser recognizes it as valid
                "visible": True
            }
        )
        
        # "VALUABLES" or "TREASURES" - only items with treasure value > 0
        valuables_object = GameObject(
            id="VALUABLES",
            name="valuables",
            description="A special command to act on treasure items.",
            aliases=["valuables", "treasures"],
            attributes={
                "bulk_action": True,
                "bulk_type": "valuables",
                "takeable": True,
                "visible": True
            }
        )
        
        # "POSSESSIONS" - acts on items you're carrying
        possessions_object = GameObject(
            id="POSSESSIONS",
            name="possessions",
            description="A special command to act on items you're carrying.",
            aliases=["possessions"],
            attributes={
                "bulk_action": True,
                "bulk_type": "possessions",
                "takeable": True,
                "visible": True
            }
        )
        
        # Add to objects registry
        self.object_manager.add_object(all_object)
        self.object_manager.add_object(valuables_object)
        self.object_manager.add_object(possessions_object)
        
    def _handle_bulk_action(self, verb: str, bulk_obj: 'GameObject') -> None:
        """Handle bulk actions like 'take all', 'drop valuables', etc. (canonical VALUABLES&C)."""
        bulk_type = bulk_obj.get_bulk_type()
        current_room = self.world.get_room(self.player.current_room)
        
        # Get the list of candidate objects based on bulk type
        candidate_objects = []
        
        if bulk_type == "all":
            # All visible, takeable objects in room (for TAKE) or inventory (for DROP)
            if verb == "take":
                if current_room:
                    for item_id in current_room.items:
                        obj = self.object_manager.get_object(item_id)
                        if obj and obj.is_takeable() and not obj.is_bulk_action():
                            candidate_objects.append(obj)
                    # Also check open containers in room
                    for item_id in current_room.items:
                        container = self.object_manager.get_object(item_id)
                        if container and container.is_container() and container.is_open():
                            for contained_id in container.get_contents():
                                contained_obj = self.object_manager.get_object(contained_id)
                                if contained_obj and contained_obj.is_takeable():
                                    candidate_objects.append(contained_obj)
            elif verb == "drop":
                for item_id in self.player.inventory:
                    obj = self.object_manager.get_object(item_id)
                    if obj and not obj.is_bulk_action():
                        candidate_objects.append(obj)
                        
        elif bulk_type == "valuables":
            # Only objects with treasure value > 0
            if verb == "take" and current_room:
                for item_id in current_room.items:
                    obj = self.object_manager.get_object(item_id)
                    if obj and obj.is_takeable() and obj.get_attribute("treasure_value", 0) > 0:
                        candidate_objects.append(obj)
            elif verb == "drop":
                for item_id in self.player.inventory:
                    obj = self.object_manager.get_object(item_id)
                    if obj and obj.get_attribute("treasure_value", 0) > 0:
                        candidate_objects.append(obj)
                        
        elif bulk_type == "possessions":
            # Items you're carrying (mainly for DROP)
            for item_id in self.player.inventory:
                obj = self.object_manager.get_object(item_id)
                if obj and not obj.is_bulk_action():
                    candidate_objects.append(obj)
        
        # Check if we found any objects
        if not candidate_objects:
            if bulk_type == "all":
                if verb == "take":
                    print("I don't see anything to take.")
                else:
                    print("You aren't carrying anything.")
            elif bulk_type == "valuables":
                print("I couldn't find any valuables.")
            else:
                print("I couldn't find anything.")
            return
        
        # Check for too many objects (canonical limit)
        max_bulk_objects = 20  # Reasonable limit to prevent spam
        if len(candidate_objects) > max_bulk_objects:
            print("I can't do everything, because I ran out of room.")  # Canonical message
            candidate_objects = candidate_objects[:max_bulk_objects]
        
        # Process each object
        success_count = 0
        for obj in candidate_objects:
            if verb == "take":
                if self._try_bulk_take(obj):
                    success_count += 1
            elif verb == "drop":
                if self._try_bulk_drop(obj):
                    success_count += 1
        
        # Summary message
        if success_count == 0:
            print("Nothing was accomplished.")
        elif success_count == 1:
            print("Done.")
        else:
            print(f"Done. ({success_count} objects affected)")
            
    def _try_bulk_take(self, obj: 'GameObject') -> bool:
        """Try to take an object as part of bulk action. Returns True if successful."""
        # Check if player can carry it
        if self.player.is_inventory_full():
            print(f"{obj.name}: Your load is too heavy.")
            return False
            
        # Find where object is located
        location_type, container_id = self._find_object_location(obj)
        
        if location_type == "inventory":
            # Already have it
            return False
        elif location_type == "room":
            # Take from room
            current_room = self.world.get_room(self.player.current_room)
            if current_room:
                current_room.remove_item(obj.id)
                self.player.add_to_inventory(obj.id)
                print(f"{obj.name}: Taken.")
                return True
        elif location_type == "container":
            # Take from container
            container = self.object_manager.get_object(container_id) if container_id else None
            if container and container.is_open():
                container.remove_from_container(obj.id)
                self.player.add_to_inventory(obj.id)
                print(f"{obj.name}: Taken.")
                return True
            elif container and not container.is_open():
                print(f"{obj.name}: The {container.name} is closed.")
                return False
                
        return False
        
    def _try_bulk_drop(self, obj: 'GameObject') -> bool:
        """Try to drop an object as part of bulk action. Returns True if successful."""
        if obj.id in self.player.inventory:
            current_room = self.world.get_room(self.player.current_room)
            if current_room:
                self.player.remove_from_inventory(obj.id)
                current_room.add_item(obj.id)
                print(f"{obj.name}: Dropped.")
                return True
        return False

    def _create_initial_world(self) -> None:
        """Create minimal fallback world if .mud files fail to load."""
        if self.debug_mode:
            print("Creating minimal fallback world...")
        else:
            print("The Implementers are improvising a simple realm...")
        
        # Create basic West of House for fallback
        west_house = Room(
            id="WHOUS", 
            name="West of House",
            description="You are standing in an open field west of a white house, with a boarded front door.",
            exits={}
        )
        self.world.add_room(west_house)
        
        # Create basic objects via ObjectLoader even in fallback
        object_loader = ZorkObjectLoader(self.object_manager, self.world)
        object_loader._create_canonical_objects()
        object_count = len(self.object_manager.objects)
        print(f"✓ Created {object_count} fallback objects")
        
        # Delete this massive method content and replace with simple fallback
        # Since the rest of the method is 450+ lines of old test world code

    # ========== Save/Load System ==========

    def save_game(self, filename: str = None) -> bool:
        """
        Save the current game state to a file.
        
        Args:
            filename: Optional filename. If not provided, generates timestamp-based name.
            
        Returns:
            True if save was successful, False otherwise.
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"zork_save_{timestamp}.json"
        
        # Sanitize filename to prevent path traversal attacks
        sanitized_filename = self._sanitize_filename(filename)
        if not sanitized_filename:
            print("Invalid filename provided.")
            return False
        
        try:
            game_state = self._collect_game_state()
            
            # Ensure saves directory exists
            saves_dir = Path("saves")
            saves_dir.mkdir(exist_ok=True)
            
            # Use sanitized filename and ensure it resolves within saves directory
            save_path = saves_dir / sanitized_filename
            
            # Security check: ensure resolved path is within saves directory
            if not self._is_safe_path(save_path, saves_dir):
                print("Invalid save path detected.")
                return False
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            
            print(f"Game saved as {save_path}")
            return True
            
        except (IOError, OSError) as e:
            logging.warning(f"IO error saving game: {type(e).__name__}")
            print("Failed to save game: IO error.")
            return False
        except json.JSONEncodeError as e:
            logging.warning(f"JSON encoding error saving game: {type(e).__name__}")
            print("Failed to save game: encoding error.")
            return False
        except Exception as e:
            logging.warning(f"Unexpected error saving game: {type(e).__name__}")
            print("Failed to save game: unexpected error.")
            return False
    
    def load_game(self, filename: str) -> bool:
        """
        Load a game state from a file.
        
        Args:
            filename: Name of the save file to load.
            
        Returns:
            True if load was successful, False otherwise.
        """
        # Sanitize filename to prevent path traversal attacks
        sanitized_filename = self._sanitize_filename(filename)
        if not sanitized_filename:
            print("Invalid filename provided.")
            return False
            
        try:
            saves_dir = Path("saves")
            save_path = saves_dir / sanitized_filename
            
            # Security check: ensure resolved path is within saves directory
            if not self._is_safe_path(save_path, saves_dir):
                print("Invalid save path detected.")
                return False
            
            if not save_path.exists():
                print(f"Save file {sanitized_filename} not found.")
                return False
            
            # Additional security: check file size to prevent memory exhaustion
            if save_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                print("Save file too large.")
                return False
            
            with open(save_path, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            
            # Validate loaded data structure
            if not self._validate_game_state(game_state):
                print("Invalid save file format.")
                return False
            
            self._restore_game_state(game_state)
            print(f"Game loaded from {save_path}")
            return True
            
        except (IOError, OSError) as e:
            logging.warning(f"IO error loading game: {type(e).__name__}")
            print("Failed to load game: file access error.")
            return False
        except json.JSONDecodeError as e:
            logging.warning(f"JSON decode error loading game: {type(e).__name__}")
            print("Failed to load game: invalid file format.")
            return False
        except Exception as e:
            logging.warning(f"Unexpected error loading game: {type(e).__name__}")
            print("Failed to load game: unexpected error.")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other security issues.
        
        Args:
            filename: Raw filename from user input
            
        Returns:
            Sanitized filename, or empty string if invalid
        """
        if not filename or not isinstance(filename, str):
            return ""
        
        # Remove any directory separators and path traversal attempts
        filename = filename.replace('/', '').replace('\\', '')
        filename = filename.replace('..', '').replace('~', '')
        
        # Remove null bytes and other dangerous characters
        filename = ''.join(c for c in filename if ord(c) > 31 and c not in '<>:"|?*')
        
        # Ensure filename doesn't start with dots or dashes
        filename = filename.lstrip('.-')
        
        # Limit length
        filename = filename[:100]
        
        # Ensure it has valid extension
        if not filename.endswith('.json'):
            if '.' in filename:
                filename = filename.split('.')[0] + '.json'
            else:
                filename = filename + '.json'
        
        # Final validation - only allow alphanumeric, underscore, dash, and dots
        if not re.match(r'^[a-zA-Z0-9_.-]+\.json$', filename):
            return ""
            
        return filename
    
    def _is_safe_path(self, path: Path, base_dir: Path) -> bool:
        """
        Check if a path is safe (within the expected directory).
        
        Args:
            path: Path to check
            base_dir: Base directory that path should be within
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            # Resolve both paths to handle any symlinks or relative components
            resolved_path = path.resolve()
            resolved_base = base_dir.resolve()
            
            # Check if the resolved path is within the base directory
            return str(resolved_path).startswith(str(resolved_base))
        except (OSError, ValueError):
            return False
    
    def _validate_game_state(self, game_state: Dict[str, Any]) -> bool:
        """
        Validate that loaded game state has expected structure and safe content.
        
        Args:
            game_state: Loaded game state data
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(game_state, dict):
            return False
        
        # Check for required top-level keys
        required_keys = ['player', 'world_state', 'score_system', 'combinations']
        if not all(key in game_state for key in required_keys):
            return False
        
        # Basic validation of player data
        if not isinstance(game_state.get('player'), dict):
            return False
        
        # Check for dangerous content that shouldn't be in save files
        game_str = json.dumps(game_state)
        dangerous_patterns = ['__import__', 'eval(', 'exec(', 'os.system', '__reduce__', '__call__']
        if any(pattern in game_str for pattern in dangerous_patterns):
            logging.warning("Dangerous content detected in save file")
            return False
        
        return True

    def _collect_game_state(self) -> Dict[str, Any]:
        """Collect all game state that needs to be saved."""
        
        # Collect world state (rooms and their items)
        world_state = {}
        for room_id, room in self.world.rooms.items():
            world_state[room_id] = {
                "items": room.items.copy(),
                "visited": room.visited,
                "flags": list(room.flags)
            }
        
        # Collect player state
        player_state = {
            "current_room": self.player.current_room,
            "inventory": self.player.inventory.copy(),
            "score": self.player.score,
            "brief_mode": self.player.brief_mode,
            "awaiting_disambiguation": self.player.awaiting_disambiguation,
            "pending_command": self.player.pending_command
        }
        
        # Collect score manager state
        score_state = {}
        if hasattr(self.score_manager, 'achievement_scores'):
            score_state = {
                "achievement_scores": self.score_manager.achievement_scores.copy(),
                "moves": self.score_manager.moves,
                "raw_score": self.score_manager.raw_score
            }
        
        # Collect combination manager state
        combination_state = {}
        if hasattr(self, 'combination_manager') and self.combination_manager:
            combination_state = self.combination_manager.save_interaction_state()
        
        # Collect puzzle manager state (if any)
        puzzle_state = {}
        if hasattr(self, 'puzzle_manager') and self.puzzle_manager:
            if hasattr(self.puzzle_manager, 'save_state'):
                puzzle_state = self.puzzle_manager.save_state()
        
        # Create complete game state
        game_state = {
            "version": "1.2.0",
            "timestamp": datetime.datetime.now().isoformat(),
            "world_state": world_state,
            "player_state": player_state,
            "score_state": score_state,
            "combination_state": combination_state,
            "puzzle_state": puzzle_state
        }
        
        return game_state
    
    def _restore_game_state(self, game_state: Dict[str, Any]) -> None:
        """Restore game state from saved data."""
        
        # Validate save version compatibility
        saved_version = game_state.get("version", "unknown")
        print(f"Loading save from version {saved_version}")
        
        # Restore world state
        if "world_state" in game_state:
            for room_id, room_data in game_state["world_state"].items():
                room = self.world.get_room(room_id)
                if room:
                    room.items = room_data.get("items", [])
                    room.visited = room_data.get("visited", False)
                    room.flags = set(room_data.get("flags", []))
        
        # Restore player state
        if "player_state" in game_state:
            player_data = game_state["player_state"]
            self.player.current_room = player_data.get("current_room", "WHOUS")
            self.player.inventory = player_data.get("inventory", [])
            self.player.score = player_data.get("score", 0)
            self.player.brief_mode = player_data.get("brief_mode", False)
            self.player.awaiting_disambiguation = player_data.get("awaiting_disambiguation", False)
            self.player.pending_command = player_data.get("pending_command", None)
        
        # Restore score manager state
        if "score_state" in game_state:
            score_data = game_state["score_state"]
            if hasattr(self.score_manager, 'achievement_scores'):
                self.score_manager.achievement_scores = score_data.get("achievement_scores", {})
                self.score_manager.moves = score_data.get("moves", 0)
                self.score_manager.raw_score = score_data.get("raw_score", 0)
        
        # Restore combination manager state
        if "combination_state" in game_state and self.combination_manager:
            combination_data = game_state["combination_state"]
            if combination_data:  # Only restore if there's data
                self.combination_manager.restore_interaction_state(combination_data)
        
        # Restore puzzle manager state
        if "puzzle_state" in game_state and self.puzzle_manager:
            puzzle_data = game_state["puzzle_state"] 
            if puzzle_data and hasattr(self.puzzle_manager, 'restore_state'):
                self.puzzle_manager.restore_state(puzzle_data)
        
        print("Game state restored successfully!")
    
    def list_saves(self) -> List[str]:
        """List all available save files."""
        saves_dir = Path("saves")
        if not saves_dir.exists():
            return []
        
        save_files = []
        for file_path in saves_dir.glob("*.json"):
            save_files.append(file_path.name)
        
        return sorted(save_files, reverse=True)  # Most recent first
    
    def _handle_save(self, command: Command) -> None:
        """Handle save command."""
        filename = None
        if command.noun:
            filename = command.noun
            if not filename.endswith('.json'):
                filename += '.json'
        
        success = self.save_game(filename)
        if not success:
            print("Save failed. Please try again.")
    
    def _handle_restore(self, command: Command) -> None:
        """Handle restore/load command."""
        if not command.noun:
            # Show available saves
            saves = self.list_saves()
            if not saves:
                print("No saved games found.")
                return
            
            print("Available saved games:")
            for i, save_file in enumerate(saves, 1):
                print(f"  {i}. {save_file}")
            print("Use 'restore <filename>' to load a specific save.")
            return
        
        filename = command.noun
        if not filename.endswith('.json'):
            filename += '.json'
        
        success = self.load_game(filename)
        if success:
            self._look_around()  # Show current location after loading
    
    # ========== NPC Command Handlers ==========
    
    def _handle_talk(self, command: Command) -> None:
        """Handle talk command."""
        if not command.noun:
            print("Talk to whom?")
            return
        
        npc = self.npc_manager.find_npc_by_name(command.noun, self.player.current_room)
        if not npc:
            print(f"I don't see {command.noun} here.")
            return
        
        dialogue_text = self.npc_manager.start_conversation(npc.id)
        if dialogue_text:
            print(dialogue_text)
        else:
            print(f"{npc.name} doesn't seem to want to talk right now.")
    
    def _handle_ask(self, command: Command) -> None:
        """Handle ask command (ask <npc> about <topic>)."""
        if not command.noun:
            print("Ask whom?")
            return
        
        if not command.noun2:
            print(f"Ask {command.noun} about what?")
            return
        
        npc = self.npc_manager.find_npc_by_name(command.noun, self.player.current_room)
        if not npc:
            print(f"I don't see {command.noun} here.")
            return
        
        topic = command.noun2
        response = self.npc_manager.ask_about_topic(npc.id, topic)
        
        if response:
            print(f"{npc.name}: \"{response}\"")
        else:
            print(f"{npc.name} doesn't know anything about that.")
    
    def _handle_greet(self, command: Command) -> None:
        """Handle greet command."""
        if not command.noun:
            # Greet all NPCs in room
            current_room = self.world.get_room(self.player.current_room)
            if not current_room:
                print("You are in an unknown location.")
                return
            
            npcs_here = self.npc_manager.get_npcs_in_room(self.player.current_room)
            if not npcs_here:
                print("There's no one here to greet.")
                return
            
            for npc in npcs_here:
                greeting = self.npc_manager.greet_npc(npc.id)
                if greeting:
                    print(f"You greet {npc.name}. {greeting}")
            return
        
        npc = self.npc_manager.find_npc_by_name(command.noun, self.player.current_room)
        if not npc:
            print(f"I don't see {command.noun} here.")
            return
        
        greeting = self.npc_manager.greet_npc(npc.id)
        if greeting:
            print(f"You greet {npc.name}. {greeting}")
        else:
            print(f"{npc.name} acknowledges your greeting.")
    
    def _handle_say(self, command: Command, user_input: str) -> None:
        """Handle say command (say "<text>")."""
        if not user_input or len(user_input.strip()) == 0:
            print("Say what?")
            return
        
        # Extract quoted text from user input
        say_match = re.search(r'say\s+"([^"]*)"', user_input.lower())
        if not say_match:
            # Try without quotes
            say_match = re.search(r'say\s+(.+)', user_input, re.IGNORECASE)
        
        if not say_match:
            print("Say what?")
            return
        
        text_to_say = say_match.group(1).strip()
        if not text_to_say:
            print("Say what?")
            return
        
        # Check if there are any NPCs in the room
        npcs_here = self.npc_manager.get_npcs_in_room(self.player.current_room)
        if not npcs_here:
            print(f"You say \"{text_to_say}\" to the empty air.")
            return
        
        print(f"You say \"{text_to_say}\"")
        
        # Let each NPC respond to what was said
        for npc in npcs_here:
            response = self.npc_manager.respond_to_speech(npc.id, text_to_say)
            if response:
                print(f"{npc.name}: \"{response}\"")
            # Note: NPCs may choose not to respond, which is fine
    
    def _create_initial_npcs(self) -> None:
        """Create canonical NPCs for the game."""
        
        # Create the canonical Thief NPC (Phase 2 of Canonical NPCs feature)
        # Start thief in a different location - let it roam to find the player
        from .entities.thief import create_canonical_thief, integrate_thief_behaviors
        thief = create_canonical_thief(self.npc_manager, starting_room="NHOUS")  # North of House
        self.npc_manager.add_npc(thief)
        
        # Integrate Thief behaviors into game engine
        integrate_thief_behaviors(self)
        
        # Create the canonical Troll NPC (Phase 3 of Canonical NPCs feature)
        from .entities.troll import create_canonical_troll, integrate_troll_behaviors
        troll = create_canonical_troll(self.npc_manager, starting_room="MTROL")  # Troll Room
        self.npc_manager.add_npc(troll)
        
        # Integrate Troll behaviors into game engine
        integrate_troll_behaviors(self)
        
        # Create the canonical Cyclops NPC (Phase 4 of Canonical NPCs feature)
        from .entities.cyclops import create_canonical_cyclops, integrate_cyclops_behaviors
        cyclops = create_canonical_cyclops()  # Located in CYCLO room
        self.npc_manager.add_npc(cyclops)
        
        # Integrate Cyclops behaviors into game engine
        integrate_cyclops_behaviors(self, self.npc_manager)
    
    # ===== COMBAT SYSTEM HANDLERS =====
    
    def _handle_attack(self, command: Command) -> None:
        """Handle attack or fight commands."""
        if not command.noun:
            print("Attack what?")
            return
        
        # Find target
        target_name = command.noun.lower()
        
        # Check for NPCs in the current room
        npcs_here = self.npc_manager.get_npcs_in_room(self.player.current_room)
        target_npc = None
        
        for npc in npcs_here:
            if (target_name in npc.name.lower() or 
                target_name in [alias.lower() for alias in npc.aliases]):
                target_npc = npc
                break
        
        if not target_npc:
            print(f"There is no {command.noun} here to attack.")
            return
        
        # Check if already in combat
        if self.combat_manager.is_in_combat(self.player.current_room):
            print("You are already engaged in combat!")
            return
        
        # Start combat
        success = self.combat_manager.start_combat(
            "player", 
            target_npc.id, 
            self.player.current_room
        )
        
        if not success:
            print("Unable to start combat at this time.")
            return
        
        # Execute the first attack
        action = self.combat_manager.execute_attack(
            self.player.combat_stats,
            target_npc.combat_stats, 
            "You",
            target_npc.name
        )
        
        print(action.description)
        
        # Check if NPC was defeated
        if not target_npc.combat_stats.is_alive():
            self.combat_manager.end_combat(self.player.current_room, winner="player")
            print(f"\nThe {target_npc.name} has been defeated!")
            
            # Handle Thief loot dropping
            if (target_npc.id == "THIEF" and hasattr(target_npc, 'thief_behavior')):
                behavior = target_npc.thief_behavior
                loot = behavior.drop_loot_on_death()
                
                if loot:
                    current_room = self.world.get_room(self.player.current_room)
                    print("\nThe thief's possessions scatter as he falls:")
                    
                    for item_id in loot:
                        obj = self.object_manager.get_object(item_id)
                        if obj and current_room:
                            current_room.add_item(item_id)
                            print(f"  A {obj.name} clatters to the ground.")
                else:
                    print("The thief had no stolen goods on him.")
            
            # Remove NPC from room (or mark as defeated)
            self.npc_manager.move_npc(target_npc.id, "DEFEATED")
            return
        
        # NPC counterattack if still alive
        counter_action = self.combat_manager.execute_attack(
            target_npc.combat_stats,
            self.player.combat_stats,
            target_npc.name,
            "You"
        )
        
        print(counter_action.description)
        
        # Check if player was defeated
        if not self.player.combat_stats.is_alive():
            self.combat_manager.end_combat(self.player.current_room, winner=target_npc.id)
            print("\nYou have been defeated! Game over.")
            self.running = False
            return
        
        print(f"\nYour health: {self.player.combat_stats.current_health}/{self.player.combat_stats.max_health}")
        print(f"{target_npc.name}'s health: {target_npc.combat_stats.current_health}/{target_npc.combat_stats.max_health}")
    
    def _handle_defend(self, command: Command) -> None:
        """Handle defend command."""
        if not self.combat_manager.is_in_combat(self.player.current_room):
            print("You are not in combat.")
            return
        
        # Defending gives temporary bonuses for the next attack
        self.player.combat_stats.block_chance += 20
        self.player.combat_stats.dodge_chance += 15
        
        print("You take a defensive stance, improving your ability to block and dodge attacks.")
        
        # Find the NPC we're fighting
        participants = self.combat_manager.get_combat_participants(self.player.current_room)
        npc_id = None
        for p in participants:
            if p != "player":
                npc_id = p
                break
        
        if not npc_id:
            print("No opponent found.")
            return
        
        target_npc = self.npc_manager.get_npc(npc_id)
        if not target_npc:
            print("Your opponent has vanished.")
            return
        
        # NPC attacks the defending player
        action = self.combat_manager.execute_attack(
            target_npc.combat_stats,
            self.player.combat_stats,
            target_npc.name,
            "You"
        )
        
        print(action.description)
        
        # Reset defensive bonuses after the attack
        self.player.combat_stats.block_chance = max(0, self.player.combat_stats.block_chance - 20)
        self.player.combat_stats.dodge_chance = max(0, self.player.combat_stats.dodge_chance - 15)
        
        # Check if player was defeated
        if not self.player.combat_stats.is_alive():
            self.combat_manager.end_combat(self.player.current_room, winner=target_npc.id)
            print("\nYou have been defeated! Game over.")
            self.running = False
            return
        
        print(f"\nYour health: {self.player.combat_stats.current_health}/{self.player.combat_stats.max_health}")
        print(f"{target_npc.name}'s health: {target_npc.combat_stats.current_health}/{target_npc.combat_stats.max_health}")
    
    def _handle_flee(self, command: Command) -> None:
        """Handle flee command."""
        if not self.combat_manager.is_in_combat(self.player.current_room):
            print("You are not in combat.")
            return
        
        success = self.combat_manager.attempt_flee("player", self.player.current_room)
        
        if success:
            print("You successfully flee from combat!")
            
            # Try to move to a random adjacent room
            current_room = self.world.get_room(self.player.current_room)
            if current_room and current_room.exits:
                import random
                exit_dir = random.choice(list(current_room.exits.keys()))
                self._handle_movement(exit_dir)
            else:
                print("But you have nowhere to flee to! You remain in place.")
        else:
            print("You attempt to flee but cannot escape!")
            
            # Find the NPC we're fighting and let them attack
            participants = self.combat_manager.get_combat_participants(self.player.current_room)
            npc_id = None
            for p in participants:
                if p != "player":
                    npc_id = p
                    break
            
            if npc_id:
                target_npc = self.npc_manager.get_npc(npc_id)
                if target_npc:
                    action = self.combat_manager.execute_attack(
                        target_npc.combat_stats,
                        self.player.combat_stats,
                        target_npc.name,
                        "You"
                    )
                    print(action.description)
                    
                    # Check if player was defeated
                    if not self.player.combat_stats.is_alive():
                        self.combat_manager.end_combat(self.player.current_room, winner=target_npc.id)
                        print("\nYou have been defeated! Game over.")
                        self.running = False

    def _handle_debug_command(self, command: Command) -> None:
        """Handle debug commands available only in debug mode."""
        if not command.noun:
            self._show_debug_menu()
            return
        
        debug_action = command.noun.lower()
        
        if debug_action == "menu":
            self._show_debug_menu()
        elif debug_action == "npc":
            self._debug_npc_system()
        elif debug_action == "combat":
            self._debug_combat_system()
        elif debug_action == "world":
            self._debug_world_info()
        elif debug_action == "objects":
            self._debug_object_info()
        else:
            print(f"Unknown debug command: {debug_action}")
            print("Try 'debug menu' for available options.")
    
    def _show_debug_menu(self) -> None:
        """Show available debug commands."""
        print("\n" + "="*50)
        print("DEBUG MENU")
        print("="*50)
        print("Available debug commands:")
        print("  debug npc     - Test NPC conversation system")
        print("  debug combat  - Test combat system")
        print("  debug world   - Show world/room information")
        print("  debug objects - Show object information")
        print("  debug menu    - Show this menu")
        print("="*50)
    
    def _debug_npc_system(self) -> None:
        """Comprehensive NPC system testing and demonstration."""
        print("\n" + "="*50)
        print("NPC SYSTEM DEBUG TEST")
        print("="*50)
        
        # Show NPCs in current room
        print("\n1. NPCs in current room:")
        npcs_here = self.npc_manager.get_npcs_in_room(self.player.current_room)
        if npcs_here:
            for npc in npcs_here:
                print(f"   - {npc.name}: {npc.description}")
        else:
            print("   No NPCs in current room.")
        
        # Show all NPCs in game
        print("\n2. All NPCs in game:")
        for npc_id, npc in self.npc_manager.npcs.items():
            room_name = "Unknown"
            room = self.world.get_room(npc.location)
            if room:
                room_name = room.name
            print(f"   - {npc.name} ({npc_id}) in {room_name}")
        
        # Test NPC interactions if NPCs are present
        if npcs_here:
            print("\n3. Testing NPC interactions:")
            
            # Test greeting
            test_npc = npcs_here[0]
            print(f"\n   Testing greet with {test_npc.name}:")
            greeting = self.npc_manager.greet_npc(test_npc.id)
            print(f"   Result: {greeting}")
            
            # Test conversation start
            print(f"\n   Testing conversation with {test_npc.name}:")
            conversation = self.npc_manager.start_conversation(test_npc.id)
            if conversation:
                print(f"   {test_npc.name}: \"{conversation}\"")
            else:
                print(f"   {test_npc.name} doesn't want to talk.")
                
            # Test topic questions
            print(f"\n   Testing topic questions with {test_npc.name}:")
            topics = ["treasure", "grue", "help", "zork"]
            for topic in topics:
                response = self.npc_manager.ask_about_topic(test_npc.id, topic)
                if response:
                    print(f"   Ask about {topic}: \"{response}\"")
                else:
                    print(f"   Ask about {topic}: No response")
            
            # Test speech responses
            print(f"\n   Testing speech responses:")
            test_phrases = ["hello", "help me", "treasure hunting"]
            for phrase in test_phrases:
                response = self.npc_manager.respond_to_speech(test_npc.id, phrase)
                if response:
                    print(f"   Say \"{phrase}\": {test_npc.name} responds \"{response}\"")
                else:
                    print(f"   Say \"{phrase}\": No response")
        
        print("\n" + "="*50)
        print("NPC DEBUG TEST COMPLETE")
        print("="*50)
        print("Try these commands in the game:")
        if npcs_here:
            npc_name = npcs_here[0].name
            print(f"  talk {npc_name}")
            print(f"  ask {npc_name} about treasure")
            print(f"  greet {npc_name}")
            print(f"  say \"hello everyone\"")
        else:
            print("  (No NPCs in current room - try 'go' to find them)")
    
    def _debug_world_info(self) -> None:
        """Show world and room debug information."""
        print("\n" + "="*50)
        print("WORLD DEBUG INFO")
        print("="*50)
        
        current_room = self.world.get_room(self.player.current_room)
        if current_room:
            print(f"Current Room: {current_room.name} ({current_room.id})")
            print(f"Description: {current_room.description}")
            print(f"Exits: {list(current_room.exits.keys())}")
            print(f"Items: {current_room.items}")
            print(f"Visited: {current_room.visited}")
            print(f"Flags: {current_room.flags}")
        
        print(f"\nTotal Rooms: {len(self.world.rooms)}")
        print(f"Total Objects: {len(self.object_manager.objects)}")
        print(f"Total NPCs: {len(self.npc_manager.npcs)}")
        
        print("\nPlayer Info:")
        print(f"  Inventory: {self.player.inventory}")
        print(f"  Score: {self.player.score}")
        print(f"  Brief Mode: {self.player.brief_mode}")
    
    def _debug_object_info(self) -> None:
        """Show object debug information."""
        print("\n" + "="*50)
        print("OBJECT DEBUG INFO")
        print("="*50)
        
        # Objects in current room
        current_room = self.world.get_room(self.player.current_room)
        if current_room and current_room.items:
            print("\nObjects in current room:")
            for item_id in current_room.items:
                obj = self.object_manager.get_object(item_id)
                if obj:
                    print(f"  - {obj.name} ({item_id}): {obj.description}")
        else:
            print("\nNo objects in current room.")
        
        # Objects in inventory
        if self.player.inventory:
            print("\nObjects in inventory:")
            for item_id in self.player.inventory:
                obj = self.object_manager.get_object(item_id)
                if obj:
                    print(f"  - {obj.name} ({item_id}): {obj.description}")
        else:
            print("\nNo objects in inventory.")
        
        print(f"\nTotal objects loaded: {len(self.object_manager.objects)}")
    
    def _debug_combat_system(self) -> None:
        """Comprehensive combat system testing and demonstration."""
        print("\n" + "="*50)
        print("COMBAT SYSTEM DEBUG TEST")
        print("="*50)
        
        # Show current combat status
        print("\n1. Current Combat Status:")
        if self.combat_manager.is_in_combat(self.player.current_room):
            status = self.combat_manager.get_combat_status(self.player.current_room)
            print(f"   Combat active in room: {self.player.current_room}")
            print(f"   Participants: {', '.join(status['participants'])}")
            print(f"   Round: {status['round_number']}")
        else:
            print("   No active combat.")
        
        # Show player combat stats
        print("\n2. Player Combat Stats:")
        stats = self.player.combat_stats
        print(f"   Health: {stats.current_health}/{stats.max_health}")
        print(f"   Attack Power: {stats.attack_power}")
        print(f"   Defense: {stats.defense}")
        print(f"   Accuracy: {stats.accuracy}%")
        print(f"   Dodge: {stats.dodge_chance}%")
        print(f"   Block: {stats.block_chance}%")
        print(f"   Critical: {stats.critical_chance}%")
        print(f"   Weapon: {stats.weapon.name if stats.weapon else 'None'}")
        
        # Show NPCs and their combat stats
        print("\n3. NPCs in current room and their combat stats:")
        npcs_here = self.npc_manager.get_npcs_in_room(self.player.current_room)
        if npcs_here:
            for npc in npcs_here:
                print(f"   {npc.name}:")
                print(f"     Health: {npc.combat_stats.current_health}/{npc.combat_stats.max_health}")
                print(f"     Attack: {npc.combat_stats.attack_power}, Defense: {npc.combat_stats.defense}")
                print(f"     Accuracy: {npc.combat_stats.accuracy}%, Dodge: {npc.combat_stats.dodge_chance}%")
        else:
            print("   No NPCs in current room.")
        
        # Show recent combat actions
        print("\n4. Recent Combat Actions:")
        recent_actions = self.combat_manager.get_recent_actions(3)
        if recent_actions:
            for action in recent_actions:
                print(f"   - {action.description}")
        else:
            print("   No recent combat actions.")
        
        # Combat testing options
        print("\n5. Combat Testing:")
        print("   Use 'attack <npc>' to start combat with an NPC")
        print("   Use 'defend' while in combat to take defensive stance")
        print("   Use 'flee' to attempt to escape from combat")
        
        # Healing option for testing
        if self.player.combat_stats.current_health < self.player.combat_stats.max_health:
            print("\n6. Debug Healing:")
            restored = self.player.combat_stats.heal(self.player.combat_stats.max_health)
            if restored > 0:
                print(f"   Player healed for {restored} health (debug mode).")
        
        print("="*50)