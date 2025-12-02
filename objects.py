"""
objects.py
General game object logic for Zork-like engine.
"""



# Canonical Zork I object attributes
canonical_attributes = {
    "osize": 1,           # Weight
    "score_value": 0,    # Points for puzzles/treasures
    "container": False,  # Can hold other objects
    "locked": False,     # Is locked
    "open": False,       # Is open
    "openable": False,   # Can be opened
    "lit": False,        # Is a light source and lit
    "takeable": True,    # Can be taken
    "wearable": False,   # Can be worn
    "edible": False,     # Can be eaten
    "weapon": False,     # Can be used as a weapon
    "portable": True,    # Can be carried
    "readable": False,   # Can be read
    "visible": True,     # Is visible
}

class GameObject:
    def __init__(self, name, description, location=None, attributes=None, osize=1, portable=True):
        self.name = name
        self.description = description
        self.location = location
        # Start with canonical attributes, update with provided
        self.attributes = canonical_attributes.copy()
        if attributes:
            self.attributes.update(attributes)
        self.osize = self.attributes.get("osize", osize)
        self.portable = self.attributes.get("portable", portable)

    def is_container(self):
        return self.attributes.get("container", False)

    def add_object(self, obj):
        if self.is_container():
            if "contents" not in self.attributes:
                self.attributes["contents"] = []
            self.attributes["contents"].append(obj)

    def remove_object(self, obj):
        if self.is_container() and "contents" in self.attributes:
            if obj in self.attributes["contents"]:
                self.attributes["contents"].remove(obj)

    def describe(self):
        desc = self.description
        # Show open/closed for openable objects
        if self.attributes.get("openable", False):
            desc += f" The {self.name} is {'open' if self.attributes.get('open', False) else 'closed'}."
        # Show contents for open containers
        if self.is_container() and self.attributes.get("open", False):
            contents = self.attributes.get("contents", [])
            if contents:
                desc += f" It contains: {', '.join([o.name for o in contents])}."
            else:
                desc += " It is empty."
        # Show other canonical attributes
        for attr, value in self.attributes.items():
            if attr in ["osize", "score_value", "container", "locked", "open", "openable", "lit", "takeable", "wearable", "edible", "weapon", "portable", "readable"]:
                if value:
                    desc += f" [{attr}: {value}]"
        return desc
