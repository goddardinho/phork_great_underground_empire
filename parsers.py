import re
from typing import Optional, List, Dict
from entities import GameObject, Room

def parse_exits(line):
    exits = {}
    matches = re.findall(r'<EXIT\s+"(\w+)"\s+"([^"]+)"', line)
    for direction, dest in matches:
        exits[direction] = dest
    return exits

def parse_objects(line):
    objects = []
    matches = re.findall(r'<OBJ\s+"([^"]+)"\s+"([^"]+)"(?:\s+([\w\s]+))?', line)
    for match in matches:
        name, desc, *rest = match
        obj = GameObject(name, desc)
        # Future: parse additional attributes from rest
        objects.append(obj)
    return objects

def parse_flags(line):
    flags = re.findall(r'<FLAGWORD\s+([\w\s]+)>', line)
    return flags[0].split() if flags else []

def parse_action(line):
    match = re.search(r'<RACTION\s+"([^"]+)"', line)
    return match.group(1) if match else None
