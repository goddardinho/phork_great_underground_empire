# Debug Scripts Directory

This directory contains standalone debugging and testing scripts that are separate from the main game's integrated debug functionality.

## Available Scripts

### `test_npc_system.py`
- **Purpose**: Standalone testing of the NPC conversation system
- **Usage**: `python3 debug_scripts/test_npc_system.py`
- **Description**: Creates test NPCs and demonstrates dialogue tree functionality independently

### `test_npc_integration.py` 
- **Purpose**: Integration testing of NPCs within the game engine
- **Usage**: `python3 debug_scripts/test_npc_integration.py`  
- **Description**: Tests NPC command handlers within the full game context

## Integrated Debug Mode (Recommended)

Instead of using these scripts, the **recommended approach** is to use the game's built-in debug mode:

```bash
python3 main.py --debug
```

Then use debug commands:
- `debug npc` - Comprehensive NPC system testing
- `debug menu` - Show all available debug commands
- `debug world` - World and room information
- `debug objects` - Object system information

## When to Use These Scripts

These standalone scripts are useful for:
- Development testing without starting the full game
- Reference implementation examples
- Isolated system testing
- Understanding NPC system internals

## Integration Notes

The functionality from these scripts has been integrated into the main game's debug mode (`debug npc` command), providing the same testing capabilities within the game environment.