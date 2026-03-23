# NPC Conversations Design Plan

## Overview
Implement basic NPC (Non-Player Character) conversation system for Zork, allowing players to interact with characters through dialogue trees and simple commands.

## Architecture

### Core Components

#### 1. NPC Entity System
```python
@dataclass
class NPC:
    id: str
    name: str
    description: str
    location: str  # Current room ID
    dialogue_tree: Dict[str, DialogueNode]
    state: Dict[str, Any]  # NPC internal state
    aliases: List[str]
    attributes: Dict[str, Any]  # moveable, friendly, etc.
```

#### 2. Dialogue System
```python
@dataclass
class DialogueNode:
    id: str
    text: str
    responses: List[DialogueResponse]
    conditions: List[Condition] = None  # State/item requirements
    effects: List[Effect] = None  # State changes after dialogue

@dataclass
class DialogueResponse:
    id: str
    text: str  # What player says
    next_node: str
    conditions: List[Condition] = None
```

#### 3. NPC Manager
```python
class NPCManager:
    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        self.dialogue_states: Dict[str, str] = {}  # npc_id -> current_node_id
    
    def get_npcs_in_room(self, room_id: str) -> List[NPC]
    def find_npc_by_name(self, name: str) -> Optional[NPC]
    def start_conversation(self, npc: NPC) -> str
    def process_dialogue_choice(self, npc_id: str, choice: str) -> str
```

## Commands

### New Commands
- `talk to [npc]` - Start conversation with NPC
- `ask [npc] about [topic]` - Ask specific questions
- `tell [npc] about [topic]` - Share information
- `say [text]` - Respond in active conversation
- `greet [npc]` - Simple greeting

### Integration with Existing Commands
- `look` - Show NPCs in room descriptions
- `examine [npc]` - Get detailed NPC description

## Canonical Zork NPCs

### Priority NPCs for Implementation
1. **Thief** - Roams dungeon, steals treasures, can be fought or bargained with
2. **Troll** - Guards bridge, demands payment or combat
3. **Cyclops** - In treasure room, can be blinded or avoided
4. **Master** - Endgame character with final challenges

### Basic Conversation Patterns
- **Greetings**: Standard responses to "hello", "hi"
- **Information**: NPCs provide hints about puzzles/locations
- **Trading**: Exchange items or information
- **State-based**: Responses change based on game progress

## Implementation Plan

### Phase 1: Core Infrastructure
1. Create NPC entity classes and manager
2. Integrate NPC system into GameEngine
3. Add NPCs to room descriptions and examine commands
4. Implement basic "talk to" command

### Phase 2: Dialogue System
1. Create dialogue tree data structures
2. Implement conversation state management
3. Add dialogue choice processing
4. Create simple dialogue trees for testing

### Phase 3: Canonical NPCs
1. Implement Thief with basic movement and theft
2. Add Troll with bridge-guarding behavior
3. Create simple dialogue trees for each NPC
4. Integrate with existing puzzle systems

### Phase 4: Advanced Features
1. NPC movement between rooms
2. State-dependent dialogue
3. Trading and item exchange
4. Combat integration (if implemented)

## File Structure

```
src/
├── entities/
│   ├── npc.py              # NPC class and related data structures
│   ├── npc_manager.py      # NPCManager class
│   └── dialogue.py         # Dialogue system classes
├── data/
│   └── npcs/
│       ├── thief.json      # Thief NPC definition
│       ├── troll.json      # Troll NPC definition
│       └── cyclops.json    # Cyclops NPC definition
└── game.py                 # Integration with GameEngine
```

## Data Format Example

```json
{
  "id": "THIEF",
  "name": "thief",
  "description": "A suspicious-looking thief lurks in the shadows.",
  "aliases": ["thief", "robber", "burglar"],
  "attributes": {
    "moveable": true,
    "hostile": false,
    "steals_treasures": true
  },
  "dialogue_tree": {
    "greeting": {
      "text": "The thief eyes you warily. 'What do you want?'",
      "responses": [
        {
          "text": "I want to trade.",
          "next_node": "trade_offer"
        },
        {
          "text": "Nothing, sorry.",
          "next_node": "dismissal"
        }
      ]
    }
  }
}
```

## Integration Points

### GameEngine Changes
```python
class GameEngine:
    def __init__(self):
        # ... existing code ...
        self.npc_manager = NPCManager()
    
    def _route_command(self, command, user_input):
        # ... existing routing ...
        elif verb == "talk":
            self._handle_talk(command)
        elif verb == "ask":
            self._handle_ask(command)
        elif verb == "greet":
            self._handle_greet(command)
```

### Room Integration
- NPCs appear in room descriptions
- NPCs can move between rooms
- NPCs can interact with room objects

## Testing Strategy

### Unit Tests
- NPC creation and management
- Dialogue tree navigation
- State management
- Command parsing

### Integration Tests
- NPC interactions with existing systems
- Room descriptions with NPCs
- Conversation flow testing

### Gameplay Tests
- Complete conversation scenarios
- NPC behavior validation
- Performance with multiple NPCs

## Success Criteria

1. **Basic Functionality**
   - Players can talk to NPCs
   - NPCs respond contextually
   - Conversation state is maintained

2. **Canonical Behavior**
   - Thief steals treasures as expected
   - Troll guards bridge properly
   - Dialogue matches Zork personality

3. **System Integration**
   - NPCs work with existing commands
   - No performance degradation
   - Proper save/load support

This design provides a solid foundation for implementing basic NPC conversations while maintaining the authentic Zork experience and integrating seamlessly with the existing codebase.