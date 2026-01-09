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
    "door": False,           # Is a door
    "transparent": False,    # Is transparent
    "indescribable": False,  # Not describable
    "drinkable": False,      # Can be drunk
    "victim": False,         # Is a victim
    "flammable": False,      # Can be set on fire
    "burning": False,        # Is on fire
    "tool": False,           # Is a tool
    "turnable": False,       # Can be turned
    "vehicle": False,        # Is a vehicle
    "reachable": False,      # Reachable from a vehicle
    "asleep": False,         # Is asleep
    "searchable": False,     # Can be searched
    "sacred": False,         # Thief can't take
    "tieable": False,        # Can be tied
    "climbable": False,      # Can be climbed
    "actor": False,          # Is an actor
    "fighting": False,       # Is in melee
    "villain": False,        # Is a villain
    "staggered": False,      # Can't fight this turn
    "dangerous": False,      # Dangerous to touch
    "collective": False,     # Collective noun
    "touched": False,        # Has been touched
    "turned_on": False,      # Light is on
    "diggable": False,       # Can be dug
    "bunch": False,          # For "all", etc.
    "trytake": False,        # Handles not being taken
    "no_check": False,       # Skip put/drop checks
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

        # User-friendly attribute display, Zork-style
        attr_labels = {
            "door": "a door",
            "transparent": "transparent",
            "edible": "edible",
            "indescribable": "indescribable",
            "drinkable": "drinkable",
            "container": "a container",
            "lit": "a light",
            "victim": "a victim",
            "flammable": "flammable",
            "burning": "burning",
            "tool": "a tool",
            "turnable": "turnable",
            "vehicle": "a vehicle",
            "reachable": "reachable from a vehicle",
            "asleep": "asleep",
            "searchable": "searchable",
            "sacred": "sacred",
            "tieable": "tieable",
            "climbable": "climbable",
            "actor": "an actor",
            "weapon": "a weapon",
            "fighting": "fighting",
            "villain": "a villain",
            "staggered": "staggered",
            "dangerous": "dangerous to touch",
            "collective": "collective noun",
            "open": "open",
            "touched": "touched",
            "turned_on": "turned on",
            "diggable": "diggable",
            "bunch": "a bunch",
            "trytake": "resists being taken",
            "no_check": "ignores put/drop checks",
            "wearable": "wearable",
            "readable": "readable",
            "takeable": "takeable",
            "portable": "portable",
        }
        shown = []
        for attr, label in attr_labels.items():
            if self.attributes.get(attr, False):
                shown.append(label)
        if shown:
            desc += " [" + ", ".join(shown) + "]"
        return desc
