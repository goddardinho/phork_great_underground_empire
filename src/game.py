"""Main game engine - Coordinates all game systems."""

from typing import Dict, List, Optional, Tuple, Any
import sys
import json
import datetime
import re
from pathlib import Path

from .world.world import World
from .world.room import Room
from .world.room_loader import ZorkRoomLoader
from .entities.player import Player
from .entities.objects import GameObject
from .parser.command_parser import CommandParser, Command
from .responses import ZorkResponses
from .puzzles import integrate_puzzles_into_game
from .score import ScoreManager
from .combinations import integrate_combinations_into_game


class GameEngine:
    """Main game engine that coordinates all game systems."""
    
    def __init__(self, use_mud_files: bool = False, mud_directory: Optional[Path] = None) -> None:
        self.world = World()
        self.player = Player()
        self.parser = CommandParser()
        self.responses = ZorkResponses()
        self.objects: Dict[str, GameObject] = {}  # object_id -> GameObject
        self.running = True
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
                   "southeast", "southwest", "up", "down"]:
            self._handle_movement(verb)
        elif verb == "go" and command.noun:
            # Handle "go north", "go east", etc.
            direction = command.noun
            if direction in ["north", "south", "east", "west", "northeast", "northwest",
                           "southeast", "southwest", "up", "down", "in", "out"]:
                self._handle_movement(direction)
            else:
                print(f"I don't know how to go {direction}.")
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
        elif verb == "save":
            self._handle_save(command)
        elif verb == "restore" or verb == "load":
            self._handle_restore(command)
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
                obj = self.objects.get(item_id)
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
            container = self.objects.get(container_id) if container_id else None
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
    
    def _handle_examine(self, command: Command) -> None:
        """Handle examine command."""
        if not command.noun:
            print("Examine what?")
            return
        
        # Find object - this will handle disambiguation if needed
        target_obj = self._find_object(command.noun)
        
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
        
        # Show base description with dynamic updates
        description = target_obj.description
        
        # Special handling for different object types
        if target_obj.id == "WINDOW":
            if target_obj.is_open():
                description = "A small window in the corner of the house. It is open, letting in fresh air."
            else:
                description = "A small window in the corner of the house. It is closed tightly."
        elif target_obj.is_container():
            # For containers, update description based on contents and state
            contents = target_obj.get_contents()
            
            # Start with base description but remove state-specific parts
            base_desc = target_obj.description
            # Remove existing state indicators
            base_desc = base_desc.replace("There appears to be something inside.", "")
            base_desc = base_desc.replace("is closed.", "").replace("is open.", "")
            
            # Add appropriate state description
            if target_obj.is_open():
                description = base_desc.strip() + " It is open."
            else:
                description = base_desc.strip() + " It is closed."
                if contents:
                    description += " There appears to be something inside."
        
        print(description)
        
        # Show container contents if it's an open container
        if target_obj.is_container() and target_obj.is_open():
            contents = target_obj.get_contents()
            if contents:
                print("It contains:")
                for item_id in contents:
                    item = self.objects.get(item_id)
                    if item:
                        print(f"  {item.name}")
            else:
                print("It is empty.")
    
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
                    item = self.objects.get(item_id)
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
            current_container = self.objects.get(current_container_id) if current_container_id else None
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
                obj = self.objects.get(item_id)
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
                container = self.objects.get(item_id)
                if container and container.is_container() and obj.id in container.get_contents():
                    return ("container", container.id)
        
        # Check if in containers in inventory
        for item_id in self.player.inventory:
            container = self.objects.get(item_id)
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
            match_obj = self.objects.get(item_id)
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
            obj = self.objects.get(item_id)
            if obj and obj.is_lit():  # Lit objects can provide heat
                heat_source = obj
                break
        
        if not heat_source:
            print("You need a heat source.")
            return
            
        # Attempt interaction
        success, message, result_obj = self.combination_manager.perform_interaction(
            primary_obj.id, heat_source.id, "heat", self.player.current_room, self.objects
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
        if not command.noun or not command.preposition_object:
            print("Combine what with what?")
            return
            
        obj1 = self._find_object(command.noun)
        obj2 = self._find_object(command.preposition_object)
        
        if not obj1 or not obj2:
            print("I can't find those objects.")
            return
            
        # Attempt combination
        success, message, result_obj = self.combination_manager.perform_interaction(
            obj1.id, obj2.id, "combine", self.player.current_room, self.objects
        )
        
        print(message)
        
        if success and result_obj:
            self._handle_object_combination(obj1.id, obj2.id, result_obj)
    
    def _handle_break_with(self, command: Command) -> None:
        """Handle break X with Y command."""
        if not command.noun or not command.preposition_object:
            print("Break what with what?") 
            return
            
        target_obj = self._find_object(command.noun)
        tool_obj = self._find_object(command.preposition_object)
        
        if not target_obj or not tool_obj:
            print("I can't find those objects.")
            return
            
        # Attempt breaking
        success, message, result_obj = self.combination_manager.perform_interaction(
            target_obj.id, tool_obj.id, "break", self.player.current_room, self.objects
        )
        
        print(message)
        
        if success and result_obj:
            self._handle_object_transformation(target_obj.id, result_obj)
    
    def _handle_pour_on(self, command: Command) -> None:
        """Handle pour X on Y command."""
        if not command.noun or not command.preposition_object:
            print("Pour what on what?")
            return
            
        liquid_obj = self._find_object(command.noun)
        target_obj = self._find_object(command.preposition_object)
        
        if not liquid_obj or not target_obj:
            print("I can't find those objects.")
            return
            
        # Attempt pouring
        success, message, result_obj = self.combination_manager.perform_interaction(
            target_obj.id, liquid_obj.id, "pour", self.player.current_room, self.objects
        )
        
        print(message)
    
    def _handle_use_tool(self, command: Command) -> None:
        """Handle use/apply X on Y command."""
        if not command.noun or not command.preposition_object:
            print("Use what on what?")
            return
            
        tool_obj = self._find_object(command.noun)  
        target_obj = self._find_object(command.preposition_object)
        
        if not tool_obj or not target_obj:
            print("I can't find those objects.")
            return
            
        # Attempt tool usage
        success, message, result_obj = self.combination_manager.perform_interaction(
            target_obj.id, tool_obj.id, "use", self.player.current_room, self.objects
        )
        
        print(message)
    
    def _handle_object_transformation(self, original_id: str, new_id: str) -> None:
        """Handle when an object transforms into another object."""
        # Remove original object from game
        original_obj = self.objects.get(original_id)
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
            container = self.objects.get(container_id)
            if container:
                container.remove_from_container(original_id)
        
        # Create and place new object (this would need the new object definition)
        # For now, just update the ID mapping
        if new_id in self.objects:
            new_obj = self.objects[new_id]
            
            # Place in same location as original
            if location_type == "inventory":
                self.player.add_to_inventory(new_id)
            elif location_type == "room":
                current_room = self.world.get_room(self.player.current_room)
                if current_room:
                    current_room.add_item(new_id)
            elif location_type == "container" and container_id:
                container = self.objects.get(container_id)
                if container:
                    container.add_to_container(new_id)
    
    def _handle_object_combination(self, obj1_id: str, obj2_id: str, result_id: str) -> None:
        """Handle when two objects are combined to create a new object."""
        # Remove both original objects
        self._remove_object_from_game(obj1_id)
        self._remove_object_from_game(obj2_id)
        
        # Add result object to inventory (most logical place for combined objects)
        if result_id in self.objects:
            self.player.add_to_inventory(result_id)
    
    def _remove_object_from_game(self, obj_id: str) -> None:
        """Remove an object from wherever it is in the game."""
        obj = self.objects.get(obj_id)
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
            container = self.objects.get(container_id)
            if container:
                container.remove_from_container(obj_id)
    
    def _find_all_objects(self, noun: str, check_inventory_only: bool = False) -> List['GameObject']:
        """Find all objects matching the given noun in accessible locations."""
        matches = []
        
        # Always check bulk action objects first (they're globally available)
        for obj_id, obj in self.objects.items():
            if obj.is_bulk_action() and obj.matches(noun):
                matches.append(obj)
        
        if check_inventory_only:
            # Only check inventory (for drop command)
            for item_id in self.player.inventory:
                obj = self.objects.get(item_id)
                if obj and obj.matches(noun) and not obj.is_bulk_action():
                    matches.append(obj)
        else:
            # Check accessible locations
            current_room = self.world.get_room(self.player.current_room)
            
            # Check current room
            if current_room:
                for item_id in current_room.items:
                    obj = self.objects.get(item_id)
                    if obj and obj.matches(noun) and not obj.is_bulk_action():
                        matches.append(obj)
                        
                    # Also check inside open containers in the room
                    if obj and obj.is_container() and obj.is_open():
                        for contained_id in obj.get_contents():
                            contained_obj = self.objects.get(contained_id)
                            if contained_obj and contained_obj.matches(noun):
                                matches.append(contained_obj)
            
            # Check inventory  
            for item_id in self.player.inventory:
                obj = self.objects.get(item_id)
                if obj and obj.matches(noun) and not obj.is_bulk_action():
                    matches.append(obj)
                
                # Also check inside open containers in inventory
                if obj and obj.is_container() and obj.is_open():
                    for contained_id in obj.get_contents():
                        contained_obj = self.objects.get(contained_id)
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
            container = self.objects.get(container_id)
            if container:
                return f"in the {container.name}"
        
        return "somewhere nearby"
    
    def _has_light_source(self) -> bool:
        """Check if player has any active light source."""
        # Check inventory for lit light sources
        for item_id in self.player.inventory:
            obj = self.objects.get(item_id)
            if obj and obj.is_lit():
                return True
        
        # Check current room for lit light sources
        current_room = self.world.get_room(self.player.current_room)
        if current_room:
            for item_id in current_room.items:
                obj = self.objects.get(item_id)
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
        
        # Check for explicitly dangerous rooms
        if current_room.has_flag("dangerous"):
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
            obj = self.objects.get(item_id)
            if obj:
                items_here.append(obj.name)
        
        if items_here:
            if len(items_here) == 1:
                print(f"There is a {items_here[0]} here.")
            else:
                print(f"There are {', '.join(items_here)} here.")
        
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
        welcome_text = """
ZORK I: The Great Underground Empire
A clean Python implementation

Type 'help' for a list of commands.
"""
        print(welcome_text)
    
    def _load_world_from_mud_files(self, mud_directory: Optional[Path] = None) -> None:
        """Load world from original Zork .mud files."""
        if mud_directory is None:
            mud_directory = Path("zork_mtl_source")
        
        if not mud_directory.exists():
            print(f"Warning: {mud_directory} not found. Creating simple test world instead.")
            self._create_initial_world()
            return
        
        print(f"Loading Zork world from {mud_directory}...")
        
        # Load rooms from .mud files
        loader = ZorkRoomLoader(self.world)
        room_count = loader.load_from_mud_files(mud_directory)
        
        if room_count == 0:
            print("Failed to load rooms from .mud files. Creating simple test world instead.")
            self._create_initial_world()
            return
        
        print(f"✓ Loaded {room_count} rooms from original Zork")
        
        # Load objects from .mud files and place them in rooms
        self._load_objects_from_mud_files(mud_directory)
        
        # Set starting room to West of House (just like original Zork)
        starting_room = "WHOUS"
        if starting_room not in self.world.rooms:
            print("Warning: Starting room WHOUS not found. Using first available room.")
            starting_room = list(self.world.rooms.keys())[0] if self.world.rooms else "UNKNOWN"
        
        # Create some basic objects for the iconic starting area
        self._create_essential_objects()
    
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
                            if obj_id in self.objects:
                                room.add_item(obj_id)
                                objects_placed += 1
                except Exception as e:
                    pass  # Continue if file can't be processed
        
        print(f"✓ Placed {objects_placed} objects in rooms")
    
    def _create_mud_objects(self) -> None:
        """Create key objects referenced in .mud files."""
        
        # Create window object (WINDO) - referenced in EHOUS and KITCH
        window = GameObject(
            id="WINDO",
            name="small window", 
            description="There is a small window here which is slightly ajar. The window appears to lead to the kitchen of the white house.",
            aliases=["window"],
            attributes={
                "takeable": False,
                "openable": True,
                "open": False,  # starts slightly ajar, can be fully opened
                "container": False,
                "door": True  # acts as passage between rooms
            }
        )
        self.objects["WINDO"] = window
        
        # Add more essential .mud objects as needed
        # TODO: Parse OBJECT definitions from .mud files automatically
    
    def _create_essential_objects(self) -> None:
        """Create essential objects like the mailbox and leaflet for the starting area."""
        
        # Create the iconic mailbox and leaflet
        mailbox = GameObject(
            id="MAILBOX",
            name="small mailbox",
            description="The small mailbox is a sturdy metal box with a hinged lid.",
            aliases=["mailbox", "box", "mail"],
            attributes={
                "takeable": False, 
                "container": True, 
                "openable": True, 
                "open": False,
                "contents": ["LEAFLET"]  # Contains the leaflet initially
            }
        )
        
        leaflet = GameObject(
            id="LEAFLET",
            name="leaflet", 
            description="A small promotional leaflet with faded text.",
            aliases=["pamphlet", "brochure", "paper", "advertisement"],
            attributes={
                "takeable": True, 
                "weight": 1,
                "readable": True,
                "readable_text": (
                    "WELCOME TO ZORK!\n\n"
                    "Zork is a game of adventure, danger, and low cunning. In it you will "
                    "explore some of the most amazing territory ever seen by mortals. No "
                    "computer should be without one!\n\n"
                    "This leaflet was found in a small mailbox."
                )
            }
        )
        
        # Add objects to world
        self.objects["MAILBOX"] = mailbox
        self.objects["LEAFLET"] = leaflet
        
        # Place mailbox in South of House (SHOUS) - the canonical location
        shous = self.world.get_room("SHOUS")
        if shous:
            shous.add_item("MAILBOX")
        else:
            # Fallback to WHOUS if SHOUS doesn't exist
            whous = self.world.get_room("WHOUS")
            if whous:
                whous.add_item("MAILBOX")
        
        # Create canonical bulk action objects
        self._create_bulk_action_objects()
        print("✓ Created essential starting objects")
        
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
        self.objects["ALL"] = all_object
        self.objects["VALUABLES"] = valuables_object
        self.objects["POSSESSIONS"] = possessions_object
        
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
                        obj = self.objects.get(item_id)
                        if obj and obj.is_takeable() and not obj.is_bulk_action():
                            candidate_objects.append(obj)
                    # Also check open containers in room
                    for item_id in current_room.items:
                        container = self.objects.get(item_id)
                        if container and container.is_container() and container.is_open():
                            for contained_id in container.get_contents():
                                contained_obj = self.objects.get(contained_id)
                                if contained_obj and contained_obj.is_takeable():
                                    candidate_objects.append(contained_obj)
            elif verb == "drop":
                for item_id in self.player.inventory:
                    obj = self.objects.get(item_id)
                    if obj and not obj.is_bulk_action():
                        candidate_objects.append(obj)
                        
        elif bulk_type == "valuables":
            # Only objects with treasure value > 0
            if verb == "take" and current_room:
                for item_id in current_room.items:
                    obj = self.objects.get(item_id)
                    if obj and obj.is_takeable() and obj.get_attribute("treasure_value", 0) > 0:
                        candidate_objects.append(obj)
            elif verb == "drop":
                for item_id in self.player.inventory:
                    obj = self.objects.get(item_id)
                    if obj and obj.get_attribute("treasure_value", 0) > 0:
                        candidate_objects.append(obj)
                        
        elif bulk_type == "possessions":
            # Items you're carrying (mainly for DROP)
            for item_id in self.player.inventory:
                obj = self.objects.get(item_id)
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
            container = self.objects.get(container_id) if container_id else None
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
        """Create a simple starting world for testing."""
        # Create West of House
        west_house = Room(
            id="WHOUS",
            name="West of House",
            description="You are standing in an open field west of a white house, with a boarded front door.",
            exits={"north": "NHOUS", "east": "HOUSE", "south": "SHOUS"}
        )
        
        # Create a few connected rooms
        north_house = Room(
            id="NHOUS",
            name="North of House", 
            description="You are facing the north side of a white house. There is no door here, and all the windows are boarded up.",
            exits={"south": "WHOUS"}
        )
        
        south_house = Room(
            id="SHOUS",
            name="South of House",
            description="You are facing the south side of a white house. There is no door here, and all the windows are boarded up.",
            exits={"north": "WHOUS"}
        )
        
        house_entrance = Room(
            id="HOUSE",
            name="Behind House", 
            description="You are behind the white house. A path leads into the forest to the east. In one corner of the house there is a small window which is slightly ajar.",
            exits={"west": "WHOUS", "east": "FOREST"}
        )
        
        # Add some test rooms with flags
        forest = Room(
            id="FOREST",
            name="Forest Path",
            description="You are on a winding path through an ancient forest. Tall trees block most of the sunlight.",
            exits={"west": "HOUSE", "down": "CAVE", "south": "TEMPLE", "southeast": "GRATE_ROOM"},
            flags={"outdoor", "noisy"}
        )
        
        cave = Room(
            id="CAVE",
            name="Dark Cave",
            description="You are in a pitch-black cave. The air is damp and cold, and you can hear water dripping somewhere in the darkness.",
            exits={"up": "FOREST", "north": "DANGER"},
            flags={"dark", "cold"}
        )
        
        temple = Room(
            id="TEMPLE",
            name="Ancient Temple",
            description="You stand before an ancient temple, its weathered stones covered in mystical symbols that seem to glow faintly.",
            exits={"north": "FOREST"},
            flags={"sacred", "outdoor"}
        )
        
        dangerous_room = Room(
            id="DANGER",
            name="Treacherous Chasm",
            description="You are on the edge of a deep, crumbling chasm. Loose rocks fall away into the darkness below at the slightest movement.",
            exits={"south": "CAVE"},
            flags={"dangerous", "dark"}
        )
        
        # Add puzzle-specific rooms
        grate_room = Room(
            id="GRATE_ROOM",
            name="Grate Clearing",
            description="You are in a small clearing. In the center is a heavy metal grate set into the ground. It appears to be locked.",
            exits={"east": "FOREST"},
            flags={"outdoor"}
        )
        
        dam_control = Room(
            id="DAM_CONTROL",
            name="Dam Control Room", 
            description="You are in the control room of Flood Control Dam #3. There is a control panel with a large metal bolt and a green plastic bubble.",
            exits={"north": "GRATE_ROOM"},
            flags={"indoor"}
        )
        
        # Add rooms to world
        self.world.add_room(west_house)
        self.world.add_room(north_house)
        self.world.add_room(south_house)
        self.world.add_room(house_entrance)
        self.world.add_room(forest)
        self.world.add_room(cave)
        self.world.add_room(temple)
        self.world.add_room(dangerous_room)
        self.world.add_room(grate_room)
        self.world.add_room(dam_control)
        
        # Create some basic objects
        mailbox = GameObject(
            id="MAILBOX",
            name="small mailbox",
            description="The small mailbox.",
            aliases=["mailbox", "box", "mail"],
            attributes={
                "takeable": False, 
                "container": True, 
                "openable": True, 
                "open": False,
                "contents": ["LEAFLET"]  # Contains the leaflet initially
            }
        )
        
        leaflet = GameObject(
            id="LEAFLET",
            name="leaflet", 
            description="A small promotional leaflet.",
            aliases=["pamphlet", "brochure", "paper", "advertisement"],
            attributes={
                "takeable": True, 
                "weight": 1,
                "readable": True,
                "readable_text": (
                    "WELCOME TO ZORK!\n\n"
                    "Zork is a game of adventure, danger, and low cunning. In it you will "
                    "explore some of the most amazing territory ever seen by mortals. No "
                    "computer should be without one!\n\n"
                    "This leaflet was found in a small mailbox."
                )
            }
        )
        
        # Window at Behind House
        window = GameObject(
            id="WINDOW",
            name="small window",
            description="A small window in the corner of the house. It is slightly ajar and looks like it could be opened wider or closed.",
            aliases=["window", "aperture"],
            attributes={
                "takeable": False,
                "openable": True,
                "open": True,  # Initially slightly ajar (open)
            }
        )
        
        # Add a torch for light source testing
        torch = GameObject(
            id="TORCH",
            name="brass torch",
            description="A sturdy brass torch with oil-soaked rags wrapped around one end. It could provide light if lit.",
            aliases=["torch", "light", "lantern"],
            attributes={
                "takeable": True,
                "weight": 2,
                "light_source": True,
                "lit": False,  # Initially unlit
                "light_turns": 50  # 50 turns of light when lit
            }
        )
        
        # Add matches to light the torch
        matches = GameObject(
            id="MATCHES",
            name="book of matches",
            description="A small book of wooden matches. There are several left.",
            aliases=["matches", "match", "book"],
            attributes={
                "takeable": True,
                "weight": 1,
                "uses_remaining": 10
            }
        )
        
        # Add test objects for disambiguation
        rusty_knife = GameObject(
            id="RUSTY_KNIFE",
            name="rusty knife",
            description="An old rusty knife with a chipped blade. It looks like it hasn't been used in years.",
            aliases=["knife", "blade", "rusty blade"],
            attributes={
                "takeable": True,
                "weight": 1
            }
        )
        
        silver_knife = GameObject(
            id="SILVER_KNIFE",
            name="silver knife",
            description="A gleaming silver knife with an ornate handle. The blade is perfectly sharp.",
            aliases=["knife", "blade", "silver blade"],
            attributes={
                "takeable": True,
                "weight": 1
            }
        )
        
        wooden_box = GameObject(
            id="WOODEN_BOX",
            name="wooden box",
            description="A simple wooden box with iron hinges. It appears to be handcrafted.",
            aliases=["box", "container", "wooden container"],
            attributes={
                "takeable": True,
                "container": True,
                "openable": True,
                "open": False,
                "contents": [],
                "weight": 2
            }
        )
        
        metal_box = GameObject(
            id="METAL_BOX",
            name="metal box",
            description="A sturdy metal box with a complex lock mechanism. It looks very secure.",
            aliases=["box", "container", "metal container"],
            attributes={
                "takeable": True,
                "container": True,
                "openable": True,
                "open": False,
                "contents": [],
                "weight": 3
            }
        )
        
        # Add objects to world
        self.objects["MAILBOX"] = mailbox
        self.objects["LEAFLET"] = leaflet
        self.objects["WINDOW"] = window
        self.objects["TORCH"] = torch
        self.objects["MATCHES"] = matches
        self.objects["RUSTY_KNIFE"] = rusty_knife
        self.objects["SILVER_KNIFE"] = silver_knife
        self.objects["WOODEN_BOX"] = wooden_box
        self.objects["METAL_BOX"] = metal_box
        
        # Add puzzle-specific objects
        rusty_keys = GameObject(
            id="KEYS",
            name="rusty keys",
            description="A small ring of old, rusty keys. They look like they might unlock something important.",
            aliases=["keys", "key", "ring"],
            attributes={
                "takeable": True,
                "weight": 1
            }
        )
        
        brass_lamp = GameObject(
            id="BRASS_LAMP",
            name="brass lamp",
            description="An elegant brass lamp with intricate engravings. It appears to be valuable.",
            aliases=["lamp", "light", "lantern"],
            attributes={
                "takeable": True,
                "weight": 3,
                "treasure": True,  # This is a treasure
                "treasure_value": 20
            }
        )
        
        jeweled_egg = GameObject(
            id="JEWELED_EGG",
            name="jeweled egg",
            description="A beautiful egg encrusted with precious gems. It gleams in the light.",
            aliases=["egg", "jewel", "gems"],
            attributes={
                "takeable": True,
                "weight": 1,
                "treasure": True,
                "treasure_value": 30
            }
        )
        
        # Additional canonical treasures from original Zork
        bauble = GameObject(
            id="BAUBLE",
            name="beautiful bauble",
            description="A delicate ornamental bauble that sparkles with inner light.",
            aliases=["bauble", "ornament"],
            attributes={
                "takeable": True,
                "weight": 1,
                "treasure": True
            }
        )
        
        brass_lantern = GameObject(
            id="BRASS_LANTERN", 
            name="brass lantern",
            description="An ornate brass lantern with intricate engravings. It's quite valuable.",
            aliases=["lantern", "brass"],
            attributes={
                "takeable": True,
                "weight": 2,
                "treasure": True
            }
        )
        
        coin = GameObject(
            id="COIN",
            name="large coin",
            description="A heavy gold coin with ancient inscriptions around the edge.",
            aliases=["coin", "gold"],
            attributes={
                "takeable": True,
                "weight": 1,
                "treasure": True
            }
        )
        
        painting = GameObject(
            id="PAINTING",
            name="beautiful painting",
            description="An exquisite oil painting in an ornate gold frame.",
            aliases=["painting", "picture", "art"],
            attributes={
                "takeable": True,  
                "weight": 3,
                "treasure": True
            }
        )
        
        self.objects["KEYS"] = rusty_keys
        self.objects["BRASS_LAMP"] = brass_lamp  
        self.objects["JEWELED_EGG"] = jeweled_egg
        self.objects["BAUBLE"] = bauble
        self.objects["BRASS_LANTERN"] = brass_lantern
        self.objects["COIN"] = coin
        self.objects["PAINTING"] = painting
        
        # Add combination objects for authentic Zork interactions
        bell = GameObject(
            id="BELL",
            name="small brass bell",
            description="A small brass bell with a clear, bright tone. It looks like it could be heated.",
            aliases=["bell", "brass"],
            attributes={
                "takeable": True,
                "weight": 1
            }
        )
        
        hot_bell = GameObject(
            id="HBELL",
            name="red hot brass bell",
            description="The brass bell is now red hot and too dangerous to touch with bare hands.",
            aliases=["bell", "hot", "red"],
            attributes={
                "takeable": False,  # Too hot to take
                "weight": 1
            }
        )
        
        rope = GameObject(
            id="ROPE",
            name="sturdy rope",
            description="A length of strong, braided rope. It could be useful for climbing or tying things.",
            aliases=["rope", "cord", "line"],
            attributes={
                "takeable": True,
                "weight": 2
            }
        )
        
        hook = GameObject(
            id="HOOK",
            name="iron hook",
            description="A sturdy iron hook with a sharp point. It looks like it could be attached to something.",
            aliases=["hook", "grapple", "iron"],
            attributes={
                "takeable": True,
                "weight": 1
            }
        )
        
        grappling_hook = GameObject(
            id="GRAPPLING_HOOK",
            name="grappling hook",
            description="A rope with an iron hook securely tied to the end. Perfect for climbing or reaching high places.",
            aliases=["grappling", "hook", "rope"],
            attributes={
                "takeable": True,
                "weight": 3
            }
        )
        
        crowbar = GameObject(
            id="CROWBAR",
            name="iron crowbar",
            description="A heavy iron crowbar, useful for prying things open or breaking objects.",
            aliases=["crowbar", "prybar", "bar", "iron"],
            attributes={
                "takeable": True,
                "weight": 3,
                "tool": True
            }
        )
        
        mirror = GameObject(
            id="MIRROR",
            name="ornate mirror",
            description="A beautiful ornate mirror with an elaborate silver frame. Your reflection stares back ominously.",
            aliases=["mirror", "glass", "looking"],
            attributes={
                "takeable": False,  # Too large/fragile
                "weight": 10,
                "breakable": True
            }
        )
        
        broken_mirror = GameObject(
            id="BROKEN_MIRROR",
            name="broken mirror",
            description="The mirror lies in countless sharp fragments. Seven years of bad luck, indeed.",
            aliases=["mirror", "glass", "shards", "pieces"],
            attributes={
                "takeable": False,
                "weight": 10
            }
        )
        
        self.objects["BELL"] = bell
        self.objects["HBELL"] = hot_bell
        self.objects["ROPE"] = rope
        self.objects["HOOK"] = hook
        self.objects["GRAPPLING_HOOK"] = grappling_hook
        self.objects["CROWBAR"] = crowbar
        self.objects["MIRROR"] = mirror
        self.objects["BROKEN_MIRROR"] = broken_mirror
        
        # Place objects in rooms (for simple test world)
        west_house.add_item("MAILBOX")  # Mailbox at west of house (leaflet is inside it)
        house_entrance.add_item("WINDOW")  # Window at behind house
        forest.add_item("TORCH")  # Torch in the forest
        forest.add_item("MATCHES")  # Matches in the forest
        
        # Place ambiguous objects for testing
        temple.add_item("RUSTY_KNIFE")  # Rusty knife in temple
        temple.add_item("SILVER_KNIFE")  # Silver knife in temple  
        cave.add_item("WOODEN_BOX")  # Wooden box in cave
        cave.add_item("METAL_BOX")  # Metal box in cave
        
        # Place puzzle objects
        north_house.add_item("KEYS")  # Keys at north of house
        temple.add_item("BRASS_LAMP")  # Treasure lamp in temple
        dangerous_room.add_item("JEWELED_EGG")  # Valuable egg in dangerous area
        
        # Place additional treasures around the world
        forest.add_item("BAUBLE")  # Beautiful bauble in forest
        cave.add_item("BRASS_LANTERN")  # Brass lantern in cave  
        house_entrance.add_item("COIN")  # Large coin behind house
        temple.add_item("PAINTING")  # Beautiful painting in temple
        
        # Place combination objects
        north_house.add_item("BELL")  # Brass bell at north of house
        cave.add_item("ROPE")  # Rope in cave with other equipment
        dangerous_room.add_item("HOOK")  # Iron hook in dangerous area
        forest.add_item("CROWBAR")  # Crowbar in forest with tools
        temple.add_item("MIRROR")  # Ornate mirror in temple (can be broken)
    
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
        
        try:
            game_state = self._collect_game_state()
            
            # Ensure saves directory exists
            saves_dir = Path("saves")
            saves_dir.mkdir(exist_ok=True)
            
            save_path = saves_dir / filename
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            
            print(f"Game saved as {save_path}")
            return True
            
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game(self, filename: str) -> bool:
        """
        Load a game state from a file.
        
        Args:
            filename: Name of the save file to load.
            
        Returns:
            True if load was successful, False otherwise.
        """
        try:
            save_path = Path("saves") / filename
            
            if not save_path.exists():
                print(f"Save file {filename} not found.")
                return False
            
            with open(save_path, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            
            self._restore_game_state(game_state)
            print(f"Game loaded from {save_path}")
            return True
            
        except Exception as e:
            print(f"Failed to load game: {e}")
            return False
    
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