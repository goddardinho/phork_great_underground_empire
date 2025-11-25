"""
containers.py
Container-specific logic for Zork-like engine.
"""

from objects import GameObject

class Container(GameObject):
    def __init__(self, name, description, location=None, attributes=None, osize=1, portable=True):
        if attributes is None:
            attributes = {"container": True, "openable": True, "open": False, "contents": []}
        else:
            attributes = dict(attributes)
            attributes.setdefault("container", True)
            attributes.setdefault("openable", True)
            attributes.setdefault("open", False)
            attributes.setdefault("contents", [])
        super().__init__(name, description, location, attributes, osize, portable)

    def open(self):
        if self.attributes.get("openable", False) and not self.attributes.get("open", False):
            self.attributes["open"] = True
            return f"You open the {self.name}."
        elif self.attributes.get("open", False):
            return f"The {self.name} is already open."
        else:
            return f"The {self.name} cannot be opened."

    def look_inside(self):
        if self.attributes.get("open", False):
            contents = self.attributes.get("contents", [])
            if contents:
                return f"Inside the {self.name} you see: {', '.join([o.name for o in contents])}."
            else:
                return f"The {self.name} is empty."
        else:
            return f"The {self.name} is closed."
