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
> debug npc
```

This provides real-time testing within the game environment.
