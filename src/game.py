"""Main game engine - Coordinates all game systems."""

from typing import Dict, List, Optional
import sys

from .world.world import World
from .world.room import Room
from .entities.player import Player
from .entities.objects import GameObject
from .parser.command_parser import CommandParser, Command


class GameEngine:
    """Main game engine that coordinates all game systems."""
    
    def __init__(self) -> None:
        self.world = World()
        self.player = Player()
        self.parser = CommandParser()
        self.objects: Dict[str, GameObject] = {}  # object_id -> GameObject
        self.running = True
        
        # Initialize with a basic starting area
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
        command = self.parser.parse(user_input)
        
        if not command:
            print("I don't understand that.")
            return
        
        # Route command to appropriate handler
        verb = command.verb
        
        if verb in ["north", "south", "east", "west", "northeast", "northwest", 
                   "southeast", "southwest", "up", "down"]:
            self._handle_movement(verb)
        elif verb == "look":
            self._handle_look(command)
        elif verb == "inventory":
            self._handle_inventory()
        elif verb == "take":
            self._handle_take(command)
        elif verb == "drop":
            self._handle_drop(command)
        elif verb == "q" or verb == "quit":
            self._handle_quit()
        elif verb == "help":
            self._handle_help()
        else:
            print(f"I don't know how to '{verb}'.")
    
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
                self.player.move_to_room(target_room_id)
                target_room.visited = True
                self._look_around()
            else:
                print("Error: That exit leads nowhere!")
        else:
            print("You can't go that way.")
    
    def _handle_look(self, command: Command) -> None:
        """Handle look command."""
        if command.noun:
            # Looking at specific object
            print(f"I don't see a {command.noun} here.")
        else:
            # Look around room
            self._look_around()
    
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
        
        current_room = self.world.get_room(self.player.current_room)
        if not current_room:
            return
        
        # Find object in current room
        target_obj = None
        for item_id in current_room.items:
            obj = self.objects.get(item_id)
            if obj and command.noun in obj.name.lower():
                target_obj = obj
                break
        
        if not target_obj:
            print(f"I don't see a {command.noun} here.")
            return
        
        if not target_obj.is_takeable():
            print(f"You can't take the {target_obj.name}.")
            return
        
        if self.player.is_inventory_full():
            print("You are carrying too many things.")
            return
        
        # Move object from room to inventory
        current_room.remove_item(target_obj.id)
        self.player.add_to_inventory(target_obj.id)
        print(f"Taken: {target_obj.name}")
    
    def _handle_drop(self, command: Command) -> None:
        """Handle drop command."""
        if not command.noun:
            print("Drop what?")
            return
        
        # Find object in inventory
        target_obj = None
        for item_id in self.player.inventory:
            obj = self.objects.get(item_id)
            if obj and command.noun in obj.name.lower():
                target_obj = obj
                break
        
        if not target_obj:
            print(f"You aren't carrying a {command.noun}.")
            return
        
        current_room = self.world.get_room(self.player.current_room)
        if current_room:
            self.player.remove_from_inventory(target_obj.id)
            current_room.add_item(target_obj.id)
            print(f"Dropped: {target_obj.name}")
    
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
  Actions: look, take <object>, drop <object>, inventory (or i)
  Other: help, quit (or q)

Shortcuts are available for most commands.
"""
        print(help_text)
    
    def _look_around(self) -> None:
        """Show the current room description."""
        current_room = self.world.get_room(self.player.current_room)
        if not current_room:
            print("You are in a void.")
            return
        
        print(current_room.get_description(self.player.brief_mode))
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
    
    def _show_welcome(self) -> None:
        """Show the welcome message."""
        welcome_text = """
ZORK I: The Great Underground Empire
A clean Python implementation

Type 'help' for a list of commands.
"""
        print(welcome_text)
    
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
            exits={"south": "WHOUS", "east": "NEHOUS"}
        )
        
        south_house = Room(
            id="SHOUS",
            name="South of House",
            description="You are facing the south side of a white house. There is no door here, and all the windows are boarded up.",
            exits={"north": "WHOUS", "east": "SEHOUS"}
        )
        
        house_entrance = Room(
            id="HOUSE",
            name="Behind House", 
            description="You are behind the white house. A path leads into the forest to the east. In one corner of the house there is a small window which is slightly ajar.",
            exits={"west": "WHOUS", "east": "FORES"}
        )
        
        # Add rooms to world
        self.world.add_room(west_house)
        self.world.add_room(north_house)
        self.world.add_room(south_house)
        self.world.add_room(house_entrance)
        
        # Create some basic objects
        mailbox = GameObject(
            id="MAILBOX",
            name="small mailbox",
            description="The small mailbox is closed.",
            attributes={"takeable": False, "container": True, "openable": True, "open": False}
        )
        
        leaflet = GameObject(
            id="LEAFLET",
            name="leaflet", 
            description="Welcome to Zork!\nThis is a simple implementation of the classic text adventure game.",
            attributes={"takeable": True, "weight": 1}
        )
        
        # Add objects to world
        self.objects["MAILBOX"] = mailbox
        self.objects["LEAFLET"] = leaflet
        
        # Place mailbox at west of house
        west_house.add_item("MAILBOX")