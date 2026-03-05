"""GameObject class - Represents items and objects in the game."""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class GameObject:
    """Represents an item or object in the game world."""
    
    id: str
    name: str  # What players see and type
    description: str  # Full description when examined
    attributes: Dict[str, Any] = field(default_factory=dict)
    
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
    
    def __str__(self) -> str:
        """String representation for display."""
        return self.name