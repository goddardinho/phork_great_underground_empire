"""ObjectLoader - Load game objects from .mud files and create canonical objects."""

from typing import Dict, List
from pathlib import Path
from .objects import GameObject
from .object_manager import ObjectManager


class ZorkObjectLoader:
    """Loads objects from Zork .mud files and creates canonical objects."""
    
    def __init__(self, object_manager: ObjectManager, world=None, debug_mode: bool = False) -> None:
        self.object_manager = object_manager
        self.world = world
        self.debug_mode = debug_mode
    
    def load_from_mud_files(self, mud_directory: Path) -> int:
        """Load objects from .mud files. Returns number of objects loaded."""
        
        # First create all canonical objects that are essential
        self._create_canonical_objects()
        
        # TODO: Parse OBJECT definitions from .mud files
        # This would parse objects like:
        # <OBJECT ["NEST"] ["BIRDS" "SMALL"] "birds nest" ...>
        # For now, we rely on canonical object creation
        
        return len(self.object_manager.objects)
    
    def _create_canonical_objects(self) -> None:
        """Create essential canonical objects referenced in rooms."""
        
        # Essential starting objects
        self._create_mailbox_and_leaflet()
        self._create_window()
        
        # Tree room objects  
        self._create_tree_objects()
        
        # Living room objects
        self._create_living_room_objects()
        
        # Kitchen objects
        self._create_kitchen_objects()
        
        # Other canonical objects
        self._create_grate()
        self._create_torch()
        self._create_garlic()
        
        # Place all objects in their canonical locations
        self._place_objects_in_rooms()
        
        # Place all objects in their canonical locations
        self._place_objects_in_rooms()
    
    def _create_mailbox_and_leaflet(self) -> None:
        """Create the iconic mailbox and leaflet."""
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
                "contents": ["LEAFLET"]
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
        
        self.object_manager.add_object(mailbox)
        self.object_manager.add_object(leaflet)
    
    def _create_window(self) -> None:
        """Create window object referenced in EHOUS and KITCH."""
        window = GameObject(
            id="WINDO",
            name="small window", 
            description="There is a small window here which is slightly ajar. The window appears to lead to the kitchen of the white house.",
            aliases=["window"],
            attributes={
                "takeable": False,
                "openable": True,
                "open": True,  # Starts slightly ajar (canonically open)
                "container": False,
                "door": True  # acts as passage between rooms
            }
        )
        self.object_manager.add_object(window)
    
    def _create_tree_objects(self) -> None:
        """Create nest, egg, and tree objects for TREE room."""
        nest = GameObject(
            id="NEST",
            name="birds nest",
            description="There is a small birds nest here.",
            aliases=["nest", "bird", "birds", "small"],
            attributes={
                "takeable": True,
                "weight": 1,
                "container": True,
                "openable": True, 
                "open": True,  # Bird's nest starts open so egg is visible
                "contents": ["EGG"],
                "capacity": 1
            }
        )
        
        egg = GameObject(
            id="EGG",
            name="jewel-encrusted egg",
            description="There is a jewel-encrusted egg here.",
            aliases=["egg", "jewel", "encrusted", "birds", "bird"],
            attributes={
                "takeable": True,
                "weight": 1,
                "treasure": True,
                "treasure_value": 5,  # Original OFVAL 5
                "container": True,
                "openable": True,
                "open": False,
                "contents": []
            }
        )
        
        tree = GameObject(
            id="TTREE", 
            name="large tree",
            description="A large tree with sturdy, climbable branches.",
            aliases=["tree", "large", "big", "tall"],
            attributes={
                "takeable": False,
                "weight": 1000
            }
        )
        
        self.object_manager.add_object(nest)
        self.object_manager.add_object(egg)
        self.object_manager.add_object(tree)
    
    def _create_living_room_objects(self) -> None:
        """Create Living Room canonical objects."""
        trophy_case = GameObject(
            id="TCASE",
            name="trophy case",
            description="A large trophy case, displaying various trophies.",
            aliases=["case", "trophy", "trophies", "display"],
            attributes={
                "takeable": False,
                "container": True,
                "openable": True,
                "open": False,
                "contents": [],
                "capacity": 10,
                "weight": 100
            }
        )
        
        rug = GameObject(
            id="RUG",
            name="large oriental rug",
            description="A large oriental rug with beautiful patterns.",
            aliases=["rug", "carpet", "oriental", "large"],
            attributes={
                "takeable": False,
                "weight": 50,
                "moveable": True
            }
        )
        
        sword = GameObject(
            id="SWORD", 
            name="elvish sword",
            description="A beautiful elvish sword of ancient make. The blade is gleaming and sharp.",
            aliases=["sword", "blade", "elvish", "weapon"],
            attributes={
                "takeable": True,
                "weight": 3,
                "weapon": True,
                "treasure": True,
                "treasure_value": 10
            }
        )
        
        brass_lamp = GameObject(
            id="LAMP",
            name="brass lamp",
            description="A brass lamp of ancient design.",
            aliases=["lamp", "light", "brass", "lantern"],
            attributes={
                "takeable": True,
                "weight": 2,
                "light_source": True,
                "lit": False,
                "light_turns": 330,
                "treasure": True,
                "treasure_value": 10
            }
        )
        
        self.object_manager.add_object(trophy_case)
        self.object_manager.add_object(rug)
        self.object_manager.add_object(sword)
        self.object_manager.add_object(brass_lamp)
    
    def _create_kitchen_objects(self) -> None:
        """Create Kitchen objects."""
        bottle = GameObject(
            id="BOTTL",
            name="glass bottle",
            description="A clear glass bottle.",
            aliases=["bottle", "glass", "container"],
            attributes={
                "takeable": True,
                "weight": 1,
                "container": True,
                "openable": False,
                "open": True,
                "contents": [],
                "capacity": 1
            }
        )
        
        sack = GameObject(
            id="SBAG",
            name="brown sack",
            description="A large brown sack bag.",
            aliases=["sack", "bag", "brown", "large"],
            attributes={
                "takeable": True,
                "weight": 1,
                "container": True,
                "openable": True,
                "open": False,
                "contents": ["GARLIC"],
                "capacity": 5
            }
        )
        
        self.object_manager.add_object(bottle)
        self.object_manager.add_object(sack)
    
    def _create_grate(self) -> None:
        """Create grate object for MGRAT."""
        grate = GameObject(
            id="GRATE",
            name="metal grate",
            description="A metal grate set into the ground.",
            aliases=["grate", "grating", "metal", "grid"],
            attributes={
                "takeable": False,
                "openable": True,
                "open": False,
                "locked": True,
                "weight": 100,
                "door": True
            }
        )
        self.object_manager.add_object(grate)
    
    def _create_torch(self) -> None:
        """Create torch object - moveable light source."""
        torch = GameObject(
            id="TORCH", 
            name="wooden torch",
            description="A wooden torch with an oil-soaked rag at one end.",
            aliases=["torch", "wooden", "light"],
            attributes={
                "takeable": True,
                "weight": 1,
                "light_source": True,
                "lit": False,
                "light_turns": 50
            }
        )
        self.object_manager.add_object(torch)
    
    def _create_garlic(self) -> None:
        """Create garlic object (often in sack).""" 
        garlic = GameObject(
            id="GARLIC",
            name="clove of garlic",
            description="A pungent clove of garlic.",
            aliases=["garlic", "clove"],
            attributes={
                "takeable": True,
                "weight": 1
            }
        )
        self.object_manager.add_object(garlic)
    
    def _place_objects_in_rooms(self) -> None:
        """Place canonical objects in their correct starting locations."""
        if not self.world:
            return
            
        object_placements = {
            # Starting objects
            "MAILBOX": "SHOUS",  # Mailbox at South of House (canonical location)
            
            # Living Room objects
            "TCASE": "LROOM",   # Trophy case in Living Room
            "RUG": "LROOM",     # Rug in Living Room  
            "SWORD": "LROOM",   # Sword in Living Room
            "LAMP": "LROOM",    # Lamp in Living Room
            
            # Kitchen objects
            "BOTTL": "KITCH",   # Bottle in Kitchen
            "SBAG": "KITCH",    # Sack in Kitchen
            
            # Tree room objects
            "NEST": "TREE",     # Nest in Tree room
            "TTREE": "TREE",    # Tree in Tree room
            
            # Other locations
            "WINDO": "EHOUS",   # Window at Behind House
            "GRATE": "MGRAT",   # Grate at Grating Room
            "TORCH": "ATTIC",   # Torch in Attic (canonical location)
        }
        
        objects_placed = 0
        for obj_id, room_id in object_placements.items():
            room = self.world.get_room(room_id)
            if room and self.object_manager.get_object(obj_id):
                room.add_item(obj_id)
                objects_placed += 1
        
        if self.debug_mode:
            print(f"✓ Placed {objects_placed} canonical objects in rooms")