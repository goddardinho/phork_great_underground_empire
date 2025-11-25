"""
containers.py
Container-specific logic for Zork-like engine.
"""

from objects import GameObject



class Container(GameObject):
    def __init__(self, name, description, location=None, attributes=None, osize=1, portable=True, max_weight=None, max_items=None):
        if attributes is None:
            attributes = {"container": True, "openable": True, "open": False, "contents": [], "locked": False}
        else:
            attributes = dict(attributes)
            attributes.setdefault("container", True)
            attributes.setdefault("openable", True)
            attributes.setdefault("open", False)
            attributes.setdefault("contents", [])
            attributes.setdefault("locked", False)
        super().__init__(name, description, location, attributes, osize, portable)
        self.max_weight = max_weight
        self.max_items = max_items

    def open(self):
        if self.attributes.get("locked", False):
            return f"The {self.name} is locked."
        if self.attributes.get("openable", False) and not self.attributes.get("open", False):
            self.attributes["open"] = True
            return f"You open the {self.name}."
        elif self.attributes.get("open", False):
            return f"The {self.name} is already open."
        else:
            return f"The {self.name} cannot be opened."

    def close(self):
        if self.attributes.get("open", False):
            self.attributes["open"] = False
            return f"You close the {self.name}."
        else:
            return f"The {self.name} is already closed."

    def lock(self):
        if self.attributes.get("locked", False):
            return f"The {self.name} is already locked."
        self.attributes["locked"] = True
        return f"You lock the {self.name}."

    def unlock(self):
        if not self.attributes.get("locked", False):
            return f"The {self.name} is already unlocked."
        self.attributes["locked"] = False
        return f"You unlock the {self.name}."

    def can_add(self, obj):
        if self.max_items is not None and len(self.attributes["contents"]) >= self.max_items:
            return False, f"The {self.name} can't hold any more items."
        if self.max_weight is not None:
            total_weight = sum(getattr(o, "osize", 1) for o in self.attributes["contents"])
            if total_weight + getattr(obj, "osize", 1) > self.max_weight:
                return False, f"The {self.name} can't hold any more weight."
        return True, None

    def add_object(self, obj):
        can_add, msg = self.can_add(obj)
        if not can_add:
            return msg
        self.attributes["contents"].append(obj)
        obj.location = self
        return f"You put the {obj.name} in the {self.name}."

    def remove_object(self, obj):
        if obj in self.attributes["contents"]:
            self.attributes["contents"].remove(obj)
            obj.location = None
            return f"You take the {obj.name} from the {self.name}."
        return f"There is no {obj.name} in the {self.name}."

    def look_inside(self, recursive=False, depth=1):
        if not self.attributes.get("open", False):
            return f"The {self.name} is closed."
        contents = self.attributes.get("contents", [])
        if not contents:
            return f"The {self.name} is empty."
        desc = f"Inside the {self.name} you see:"
        for obj in contents:
            desc += f"\n- {obj.name}: {obj.description}"
            if recursive and hasattr(obj, "is_container") and obj.is_container() and depth > 0:
                desc += "\n  " + obj.look_inside(recursive=True, depth=depth-1)
        return desc
