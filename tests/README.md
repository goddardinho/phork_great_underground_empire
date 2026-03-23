# Tests Directory

This directory contains all unit tests, integration tests, debug scripts, and validation tools for the project.

## Running Tests

### All Tests
```
python3 -m unittest discover tests
```

### Individual Test Files
```
python3 tests/test_room_flags.py
```

## Debug and Integration Scripts

### NPC System Testing
- `test_npc_system.py` - Standalone NPC conversation system testing
- `test_npc_integration.py` - NPC integration testing within game engine
- `test_combat_system.py` - Complete combat system testing (Phase 1)
- `test_thief_npc.py` - Canonical Thief NPC testing with 11 comprehensive tests (Phase 2)

### Validation Scripts
- `validate_canonical.py`, `validate_canonical_objects.py` - Canonical accuracy validation
- `debug_connectivity.py`, `repair_connectivity.py` - World connectivity analysis
- `room_wiring_auditor.py` - Comprehensive room connection auditing

### Analysis Tools
- `analyze_*.py` files - Various system analysis scripts
- Performance and security test suites

## Preferred Testing Method

For NPC testing, use the integrated debug mode instead of standalone scripts:
```
python3 main.py --debug
> debug npc      # General NPC system testing
> debug combat   # Combat system validation 
> debug thief    # Thief NPC behavior testing
```

Additional standalone debug tools (run from project root):
```
python tests/debug_thief_npc.py           # Comprehensive Thief validation
python tests/test_thief_interactive.py    # Interactive Thief gameplay testing
```

This provides real-time testing within the game environment.
