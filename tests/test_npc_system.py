#!/usr/bin/env python3
"""Test script for the NPC conversation system."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.entities.npc_manager import NPCManager
from src.entities.npc import NPC, DialogueNode, DialogueResponse


def create_test_npcs(npc_manager: NPCManager) -> None:
    """Create some test NPCs for demonstration."""
    
    # Create a simple NPC (Hermit)
    hermit = npc_manager.create_simple_npc(
        npc_id="HERMIT",
        name="hermit",
        description="An old hermit sits here, studying an ancient tome.",
        location="WHOUS",  # West of House
        greeting_text="The hermit looks up from his book and nods quietly.",
        aliases=["old hermit", "old man", "scholar"]
    )
    print(f"✓ Created {hermit.name}")
    
    # Create a more complex NPC (Wise Oracle)
    oracle_greeting = DialogueNode(
        id="greeting",
        text="The Oracle speaks: 'I sense you seek knowledge, traveler. What brings you to my presence?'",
        responses=[
            DialogueResponse(
                id="resp_treasure",
                text="I seek treasure",
                next_node="treasure_advice"
            ),
            DialogueResponse(
                id="resp_grue",
                text="I need help with the grue",
                next_node="grue_warning"
            ),
            DialogueResponse(
                id="resp_place",
                text="Tell me about this place",
                next_node="place_info"
            )
        ]
    )
    
    treasure_node = DialogueNode(
        id="treasure_advice",
        text="'Treasure, you say? The Great Underground Empire holds many riches, but they come with great peril. Look for the brass lantern first - light will be your salvation in the dark passages.'",
        end_conversation=True
    )
    
    grue_node = DialogueNode(
        id="grue_warning",
        text="'Ah, the grues! Creatures of absolute darkness they are. They cannot survive in even the faintest light. Carry a source of illumination always, and you shall be safe.'",
        end_conversation=True
    )
    
    place_node = DialogueNode(
        id="place_info",
        text="'This is the entrance to the Great Underground Empire, built by the Implementers of old. Many passages lie beneath, filled with wonders and terrors alike.'",
        end_conversation=True
    )
    
    oracle = NPC(
        id="ORACLE",
        name="oracle",
        description="A mysterious Oracle sits here, surrounded by swirling mists.",
        location="WHOUS",
        dialogue_tree={
            "greeting": oracle_greeting,
            "treasure_advice": treasure_node,
            "grue_warning": grue_node,
            "place_info": place_node
        },
        aliases=["wise oracle", "mysterious oracle", "seer"],
        attributes={
            "moveable": False,
            "friendly": True,
            "wise": True
        }
    )
    npc_manager.add_npc(oracle)
    print(f"✓ Created {oracle.name} with interactive dialogue tree")


def test_npc_interactions(npc_manager: NPCManager) -> None:
    """Test various NPC interactions."""
    
    print("\n" + "="*50)
    print("TESTING NPC SYSTEM")
    print("="*50)
    
    # Test finding NPCs
    print("\n1. Finding NPCs in West of House:")
    npcs_here = npc_manager.get_npcs_in_room("WHOUS")
    for npc in npcs_here:
        print(f"   - {npc.name}: {npc.description}")
    
    # Test simple conversation
    print("\n2. Starting conversation with hermit:")
    hermit_response = npc_manager.start_conversation("HERMIT")
    print(f"   {hermit_response}")
    
    # Test asking about topics
    print("\n3. Asking hermit about treasure:")
    response = npc_manager.ask_about_topic("HERMIT", "treasure")
    print(f"   Hermit: \"{response}\"" if response else "   The hermit doesn't respond.")
    
    # Test greeting
    print("\n4. Greeting the oracle:")
    greeting = npc_manager.greet_npc("ORACLE")
    print(f"   {greeting}")
    
    # Test speech response
    print("\n5. Saying 'Hello everyone!':")
    for npc in npcs_here:
        response = npc_manager.respond_to_speech(npc.id, "Hello everyone!")
        if response:
            print(f"   {npc.name}: \"{response}\"")
    
    # Test detailed conversation with Oracle
    print("\n6. Complex conversation with Oracle:")
    oracle_greeting = npc_manager.start_conversation("ORACLE")
    print(f"   Oracle: \"{oracle_greeting}\"")
    
    print("\n7. Oracle dialogue tree structure:")
    oracle = npc_manager.get_npc("ORACLE")
    if oracle:
        greeting_node = oracle.get_greeting_node()
        if greeting_node and greeting_node.responses:
            print("   Available responses:")
            for i, response in enumerate(greeting_node.responses, 1):
                print(f"     {i}. {response.text}")


def main():
    """Main test function."""
    print("NPC Conversation System Test")
    print("="*30)
    
    # Initialize NPC manager
    npc_manager = NPCManager()
    
    # Create test NPCs
    print("Creating test NPCs...")
    create_test_npcs(npc_manager)
    
    # Test interactions
    test_npc_interactions(npc_manager)
    
    print("\n" + "="*50)
    print("NPC SYSTEM TEST COMPLETE")
    print("="*50)
    print("\nTo test in the actual game, start the game and try:")
    print("  talk hermit")
    print("  ask hermit about treasure") 
    print("  greet oracle")
    print("  say \"hello everyone\"")


if __name__ == "__main__":
    main()