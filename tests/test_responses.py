#!/usr/bin/env python3
"""Quick test of the snarky response system."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.responses import ZorkResponses

def demo_responses():
    resp = ZorkResponses()

    print('🎭 === EASTER EGG RESPONSES ===')
    print(f'xyzzy → {resp.get_special_command_response("xyzzy")}')
    print(f'plugh → {resp.get_special_command_response("plugh")}')  
    print(f'hello → {resp.get_special_command_response("hello")}')
    print(f'jump → {resp.get_special_command_response("jump")}')
    print(f'curse → {resp.get_special_command_response("curse")}')

    print('\n🤔 === UNKNOWN COMMAND VARIETY ===')  
    for i in range(4):
        print(f'blahblah #{i+1} → {resp.get_unknown_command_response("blahblah")}')

    print('\n🚫 === MOVEMENT RESPONSES ===')
    for i in range(4):
        print(f'blocked move #{i+1} → {resp.get_cant_go_response()}')

    print('\n🔍 === OBJECT NOT FOUND ===')
    for i in range(4):
        print(f'missing sword #{i+1} → {resp.get_dont_see_object_response("sword")}')

    print('\n📦 === INVENTORY RESPONSES ===')
    print(f'empty hands → {resp.get_inventory_response("empty_inventory")}')
    print(f'already have → {resp.get_inventory_response("already_have", "lamp")}')
    print(f'dont have → {resp.get_inventory_response("dont_have")}')

    print('\n✨ === VARIETY CHECK: Same command, different responses ===')  
    for i in range(3):
        print(f'"foobar" try #{i+1} → {resp.get_unknown_command_response("foobar")}')

    print('\n✅ === TESTING COMPLETE ===')
    print('Response system shows excellent variety and personality!')

if __name__ == "__main__":
    demo_responses()