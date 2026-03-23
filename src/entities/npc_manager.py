"""NPC Manager - Central registry for all NPCs and conversation handling."""

from typing import Dict, List, Optional, Tuple
from .npc import NPC, DialogueNode, DialogueResponse


class NPCManager:
    """Manages all NPCs and their conversations in the game."""
    
    def __init__(self) -> None:
        self.npcs: Dict[str, NPC] = {}
        self.dialogue_states: Dict[str, str] = {}  # npc_id -> current_node_id
        self.active_conversations: Dict[str, str] = {}  # player_id -> npc_id (for future multiplayer support)
    
    def add_npc(self, npc: NPC) -> None:
        """Add an NPC to the registry."""
        self.npcs[npc.id] = npc
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get an NPC by its ID."""
        return self.npcs.get(npc_id)
    
    def find_npc_by_name(self, name: str, room_id: str = None) -> Optional[NPC]:
        """Find an NPC that matches the given name, optionally in a specific room."""
        for npc in self.npcs.values():
            if npc.matches(name):
                if room_id is None or npc.location == room_id:
                    return npc
        return None
    
    def get_npcs_in_room(self, room_id: str) -> List[NPC]:
        """Get all NPCs currently in the specified room."""
        npcs_in_room = []
        for npc in self.npcs.values():
            if npc.location == room_id:
                npcs_in_room.append(npc)
        return npcs_in_room
    
    def move_npc(self, npc_id: str, new_room: str) -> bool:
        """Move an NPC to a new room. Returns True if successful."""
        npc = self.get_npc(npc_id)
        if npc and npc.is_moveable():
            npc.location = new_room
            return True
        return False
    
    def start_conversation_with_npc(self, npc: NPC, player_id: str = "default") -> Tuple[bool, str]:
        """
        Start a conversation with an NPC.
        Returns (success, message).
        """
        if not npc:
            return False, "I don't see anyone to talk to."
        
        greeting_node = npc.get_greeting_node()
        if not greeting_node:
            return False, f"The {npc.name} doesn't seem interested in talking."
        
        # Set up conversation state
        self.dialogue_states[npc.id] = greeting_node.id
        self.active_conversations[player_id] = npc.id
        
        # Build response message
        message = greeting_node.text
        
        # Add response options if available
        if greeting_node.responses:
            message += "\n\nYou can:"
            for i, response in enumerate(greeting_node.responses, 1):
                message += f"\n  {i}. {response.text}"
            message += "\n\nSay the number of your choice, or 'goodbye' to end the conversation."
        
        return True, message
    
    def process_dialogue_choice(self, npc_id: str, choice: str, player_id: str = "default") -> Tuple[bool, str]:
        """
        Process a dialogue choice from the player.
        Returns (success, message).
        """
        npc = self.get_npc(npc_id)
        if not npc:
            return False, "Conversation error: NPC not found."
        
        current_node_id = self.dialogue_states.get(npc_id)
        if not current_node_id:
            return False, "You're not currently in a conversation with anyone."
        
        current_node = npc.get_dialogue_node(current_node_id)
        if not current_node:
            return False, "Conversation error: Invalid dialogue state."
        
        # Handle goodbye
        if choice.lower().strip() in ["goodbye", "bye", "exit", "quit"]:
            self.end_conversation(npc_id, player_id)
            return True, f"You say goodbye to the {npc.name}."
        
        # Try to parse choice as number
        try:
            choice_num = int(choice.strip())
            if 1 <= choice_num <= len(current_node.responses):
                selected_response = current_node.responses[choice_num - 1]
                return self._handle_dialogue_response(npc, selected_response, player_id)
        except ValueError:
            pass
        
        # Try to match choice as text
        choice_lower = choice.lower().strip()
        for response in current_node.responses:
            if choice_lower in response.text.lower():
                return self._handle_dialogue_response(npc, response, player_id)
        
        return False, f"I don't understand that response. Please choose a number (1-{len(current_node.responses)}) or say 'goodbye'."
    
    def _handle_dialogue_response(self, npc: NPC, response: DialogueResponse, player_id: str) -> Tuple[bool, str]:
        """Handle a selected dialogue response."""
        # Move to next dialogue node
        next_node = npc.get_dialogue_node(response.next_node)
        if not next_node:
            self.end_conversation(npc.id, player_id)
            return True, "The conversation comes to an end."
        
        # Update dialogue state
        self.dialogue_states[npc.id] = next_node.id
        
        # Build response message
        message = next_node.text
        
        # Check if conversation should end
        if next_node.end_conversation or not next_node.responses:
            self.end_conversation(npc.id, player_id)
            return True, message
        
        # Add response options
        if next_node.responses:
            message += "\n\nYou can:"
            for i, next_response in enumerate(next_node.responses, 1):
                message += f"\n  {i}. {next_response.text}"
            message += "\n\nSay the number of your choice, or 'goodbye' to end the conversation."
        
        return True, message
    
    def end_conversation(self, npc_id: str, player_id: str = "default") -> None:
        """End a conversation with an NPC."""
        if npc_id in self.dialogue_states:
            del self.dialogue_states[npc_id]
        if player_id in self.active_conversations:
            del self.active_conversations[player_id]
    
    def get_active_conversation(self, player_id: str = "default") -> Optional[str]:
        """Get the ID of the NPC the player is currently talking to."""
        return self.active_conversations.get(player_id)
    
    def is_in_conversation(self, player_id: str = "default") -> bool:
        """Check if the player is currently in a conversation."""
        return player_id in self.active_conversations
    
    def create_simple_npc(self, npc_id: str, name: str, description: str, location: str, 
                         greeting_text: str, aliases: List[str] = None) -> NPC:
        """
        Create a simple NPC with just a greeting dialogue.
        Utility method for quick NPC creation.
        """
        if aliases is None:
            aliases = []
        
        # Create simple greeting dialogue
        greeting_node = DialogueNode(
            id="greeting",
            text=greeting_text,
            end_conversation=True
        )
        
        npc = NPC(
            id=npc_id,
            name=name,
            description=description,
            location=location,
            dialogue_tree={"greeting": greeting_node},
            aliases=aliases,
            attributes={
                "moveable": False,
                "friendly": True,
                "hostile": False
            }
        )
        
        self.add_npc(npc)
        return npc
    
    def start_conversation(self, npc_id: str, player_id: str = "default") -> Optional[str]:
        """
        Start conversation with NPC by ID.
        Returns the greeting text or None.
        """
        npc = self.get_npc(npc_id)
        if not npc:
            return None
        
        greeting_node = npc.get_greeting_node()
        if not greeting_node:
            return None
        
        # Set up conversation state
        self.dialogue_states[npc.id] = greeting_node.id
        self.active_conversations[player_id] = npc.id
        
        return greeting_node.text
    
    def ask_about_topic(self, npc_id: str, topic: str) -> Optional[str]:
        """
        Ask an NPC about a topic. Simple implementation for now.
        Returns response text or None.
        """
        npc = self.get_npc(npc_id)
        if not npc:
            return None
        
        # Simple topic matching - could be enhanced with more sophisticated AI
        topic_lower = topic.lower()
        
        # Simple responses based on topic
        if topic_lower in ["treasure", "treasures", "gold"]:
            return "I know of many treasures hidden in these passages, but you must find them yourself."
        elif topic_lower in ["grue", "grues", "darkness"]:
            return "The grues lurk in the darkness. Light is your only protection."
        elif topic_lower in ["zork", "game", "empire"]:
            return "Ah, the Great Underground Empire! Many have sought its secrets."
        elif topic_lower in ["help", "assistance"]:
            return "I can only give you advice. The rest is up to you."
        else:
            return None  # NPC doesn't know about this topic
    
    def greet_npc(self, npc_id: str) -> Optional[str]:
        """
        Greet an NPC. Returns greeting response or None.
        """
        npc = self.get_npc(npc_id)
        if not npc:
            return None
        
        if npc.attributes.get("friendly", True):
            return f"{npc.name} nods in acknowledgment."
        elif npc.attributes.get("hostile", False):
            return f"{npc.name} glares at you menacingly."
        else:
            return f"{npc.name} seems indifferent to your greeting."
    
    def respond_to_speech(self, npc_id: str, speech: str) -> Optional[str]:
        """
        Let an NPC respond to something said aloud.
        Returns response or None if NPC chooses not to respond.
        """
        npc = self.get_npc(npc_id)
        if not npc:
            return None
        
        # Simple keyword-based responses
        speech_lower = speech.lower()
        
        if any(word in speech_lower for word in ["hello", "hi", "greetings"]):
            return self.greet_npc(npc_id)
        elif any(word in speech_lower for word in ["help", "assistance"]):
            return "Perhaps I can be of assistance."
        elif any(word in speech_lower for word in ["treasure", "gold", "riches"]):
            return "Treasure, you say? There are many secrets hidden here."
        
        # NPCs may choose not to respond to random speech
        return None