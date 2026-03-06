"""GameObject class - Represents items and objects in the game."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class GameObject:
    """Represents an item or object in the game world."""
    
    id: str
    name: str  # What players see and type
    description: str  # Full description when examined
    attributes: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)  # Alternative names for this object
    
    def get_attribute(self, name: str, default: Any = None) -> Any:
        """Get an attribute value with optional default."""
        return self.attributes.get(name, default)
    
    def set_attribute(self, name: str, value: Any) -> None:
        """Set an attribute value."""
        self.attributes[name] = value
    
    def is_takeable(self) -> bool:
        """Check if this object can be picked up."""
        return self.get_attribute("takeable", False)
    
    def is_portable(self) -> bool:
        """Check if this object can be carried around."""
        return self.get_attribute("portable", True)
    
    def get_weight(self) -> int:
        """Get the object's weight (for inventory limits)."""
        return self.get_attribute("weight", 1)
    
    def is_container(self) -> bool:
        """Check if this object can contain other objects."""
        return self.get_attribute("container", False)
    
    def is_openable(self) -> bool:
        """Check if this object can be opened/closed."""
        return self.get_attribute("openable", False)
    
    def is_open(self) -> bool:
        """Check if this openable object is currently open."""
        return self.get_attribute("open", False)

    def is_locked(self) -> bool:
        """Check if this container is locked."""
        return self.get_attribute("locked", False)
        
    def can_open(self) -> bool:
        """Check if this container can currently be opened."""
        return self.is_openable() and not self.is_locked() and not self.is_open()
        
    def can_close(self) -> bool:
        """Check if this container can currently be closed."""
        return self.is_openable() and self.is_open()
        
    def get_capacity(self) -> int:
        """Get maximum number of items this container can hold (0 = unlimited)."""
        return self.get_attribute("capacity", 0)
        
    def is_at_capacity(self) -> bool:
        """Check if container is at maximum capacity."""
        capacity = self.get_capacity()
        if capacity == 0:  # Unlimited capacity
            return False
        return len(self.get_contents()) >= capacity
    
    def is_readable(self) -> bool:
        """Check if this object can be read."""
        return self.get_attribute("readable", False) or self.get_attribute("readable_text", None) is not None
    
    def is_light_source(self) -> bool:
        """Check if this object provides light."""
        return self.get_attribute("light_source", False)
    
    def is_lit(self) -> bool:
        """Check if this light source is currently providing light."""
        return self.is_light_source() and self.get_attribute("lit", False)
    
    def light_turns_remaining(self) -> int:
        """Get remaining turns of light (0 = infinite, -1 = no light)."""
        if not self.is_light_source():
            return -1
        return self.get_attribute("light_turns", 0)
    
    def get_readable_text(self) -> Optional[str]:
        """Get the text content of a readable object."""
        return self.get_attribute("readable_text", None)
    
    def add_to_container(self, item_id: str) -> bool:
        """Add an item to this container. Returns True if successful."""
        if not self.is_container():
            return False
        
        # Check capacity before adding
        if self.is_at_capacity():
            return False
        
        contents = self.get_attribute("contents", [])
        if item_id not in contents:
            contents.append(item_id)
            self.set_attribute("contents", contents)
        return True
    
    def remove_from_container(self, item_id: str) -> bool:
        """Remove an item from this container. Returns True if item was present."""
        if not self.is_container():
            return False
        
        contents = self.get_attribute("contents", [])
        try:
            contents.remove(item_id)
            self.set_attribute("contents", contents)
            return True
        except ValueError:
            return False
    
    def get_contents(self) -> List[str]:
        """Get the list of items in this container."""
        if not self.is_container():
            return []
        return self.get_attribute("contents", [])
    
    def __str__(self) -> str:
        """String representation for display."""
        return self.name
    
    def matches(self, noun: str) -> bool:
        """Check if the given noun matches this object's name or aliases."""
        noun_lower = noun.lower().strip()
        
        # Check aliases first (exact match for precision)
        for alias in self.aliases:
            if noun_lower == alias.lower():
                return True
        
        # Check primary name with refined matching rules
        name_lower = self.name.lower()
        name_words = name_lower.split()
        
        # Exact match against full name
        if noun_lower == name_lower:
            return True
            
        # Check if noun matches any complete word in the name
        for word in name_words:
            if noun_lower == word:
                return True
        
        # Allow longer substring matches (5+ chars) to catch partial but meaningful matches
        if len(noun_lower) >= 5 and noun_lower in name_lower:
            return True
                
        return False