"""
objects.py
General game object logic for Zork-like engine.
"""


class GameObject:
    def __init__(self, name, description, location=None, attributes=None, osize=1, portable=True):
        self.name = name
        self.description = description
        self.location = location
        self.attributes = attributes if attributes else {}
        self.osize = osize  # Canonical Zork I weight
        self.portable = portable

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
        if self.attributes.get("openable", False):
            desc += f" The {self.name} is {'open' if self.attributes.get('open', False) else 'closed'}."
        if self.is_container() and self.attributes.get("open", False):
            contents = self.attributes.get("contents", [])
            if contents:
                desc += f" It contains: {', '.join([o.name for o in contents])}."
            else:
                desc += " It is empty."
        return desc
