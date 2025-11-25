# Gameplay Duplication Framework - Todo List

## Current Development Focus
- See the Roadmap section in README.md for all planned and future features.
- [x] Expand parser to support all Zork I commands
- [x] Implement puzzles, NPCs, and advanced object logic
- [x] Add automated tests for movement, puzzles, and map fidelity
- [x] Add save/load functionality and more gameplay features
- [x] Implement room flags and puzzles
- [x] Add custom actions, scripted events, and game state features (score, save/restore, NPCs)
-- [ ] Gameplay parity
  - [x] Object-specific actions (e.g., mailbox, leaflet, lantern)
  - [x] Inventory limits and object weight
  - Locked doors and keys
  - Score system for puzzles and treasures
  - Multi-step puzzles and scripted events
  - NPCs (thief, troll, cyclops, etc.)
  - Death and restart logic
  - Save/load with full game state (including containers, puzzles, flags)
  - Object attributes (edible, readable, wearable, portable, etc.)
  - Room flags (dangerous, dark, visited, etc.)
  - Synonyms and flexible parser
  - Random events (thief, troll, etc.)
  - Darkness and light mechanics (grue danger) [partially complete, revisit for full parity]
  - Endgame logic and victory conditions
  - Advanced container mechanics (multiple containers, nested containers, inventory interaction)
  - Object hiding and searching (objects hidden in containers or rooms, requiring 'search' or 'examine')
  - Environmental hazards (flooding, falling, poison, etc.)
  - Map expansion (add all canonical rooms, locations, and connections)
  - Save/restore improvements (multiple slots, autosave)
  - Treasure list and scoring
  - Trap rooms and timed events
- [ ] Room/location parity
  - Ensure all rooms, locations, and connections match the original Zork I map and source.

## Completed Tasks (see CHANGELOG.md for details)
- [x] Enrich all rooms with real data, exits, objects, flags, and actions
- [x] Automate exit population from source
- [x] Validate room and exit data with map comparison script
- [x] Remove stray/duplicate room/object code
- [x] Add missing imports and class definitions for Room and GameObject
- [x] Document enrichment logic and mapping for maintainers

## Reference
- For completed milestones and version history, see CHANGELOG.md
