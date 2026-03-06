"""Main game engine - Coordinates all game systems."""

from typing import Dict, List, Optional, Tuple
import sys
from pathlib import Path

from .world.world import World
from .world.room import Room
from .world.room_loader import ZorkRoomLoader
from .entities.player import Player
from .entities.objects import GameObject
from .parser.command_parser import CommandParser, Command
from .responses import ZorkResponses


class GameEngine:
    """Main game engine that coordinates all game systems."""
    
    def __init__(self, use_mud_files: bool = False, mud_directory: Optional[Path] = None) -> None:
        self.world = World()
        self.player = Player()
        self.parser = CommandParser()
        self.responses = ZorkResponses()
        self.objects: Dict[str, GameObject] = {}  # object_id -> GameObject
        self.running = True
        
        # Initialize world from .mud files or create a basic test world
        if use_mud_files:
            self._load_world_from_mud_files(mud_directory)
        else:
            self._create_initial_world()
    
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
        elif location_type == "container":
            # Take from container
            container = self.objects.get(container_id) if container_id else None
            if container and container.is_open():
                container.remove_from_container(target_obj.id)
                self.player.add_to_inventory(target_obj.id)
                print(f"Taken: {target_obj.name}")
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
  Display: brief (short room descriptions), verbose (full room descriptions)
  Other: help, quit (or q)

Shortcuts are available for most commands.
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
            # "look" command - always show full description
            print(current_room.get_description(force_verbose=True))
        elif not current_room.visited:
            # First visit - always show full description regardless of brief mode
            print(current_room.get_description(force_verbose=True))
        else:
            # Subsequent visit - respect brief mode setting
            print(current_room.get_description(force_brief=self.player.brief_mode))
        
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
        
        # Set starting room to West of House (just like original Zork)
        starting_room = "WHOUS"
        if starting_room not in self.world.rooms:
            print("Warning: Starting room WHOUS not found. Using first available room.")
            starting_room = list(self.world.rooms.keys())[0] if self.world.rooms else "UNKNOWN"
        
        self.player.current_room = starting_room
        
        # Create some basic objects for the iconic starting area
        self._create_essential_objects()
    
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
            exits={"west": "HOUSE", "down": "CAVE", "south": "TEMPLE"},
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
        
        # Add rooms to world
        self.world.add_room(west_house)
        self.world.add_room(north_house)
        self.world.add_room(south_house)
        self.world.add_room(house_entrance)
        self.world.add_room(forest)
        self.world.add_room(cave)
        self.world.add_room(temple)
        self.world.add_room(dangerous_room)
        
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