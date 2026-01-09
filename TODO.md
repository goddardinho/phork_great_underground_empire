# Gameplay Duplication Framework - Todo List

## Buglist

- [ ] Mailbox can be 'taken' (should not be portable; not in parity with Zork I source)

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
  - [x] Locked doors and keys
  - [x] Score system for puzzles and treasures
  - [x] Multi-step puzzles and scripted events
  - [x] NPCs (thief, troll, cyclops, etc.)
  - [x] Death and restart logic
  - [x] Save/load with full game state
  - [x] Help system and command list
  - [ ] Object attributes (edible, readable, wearable, portable, etc.)
  - [ ] Room flags (dangerous, dark, visited, etc.)
  - [ ] Synonyms and flexible parser
  - [ ] Random events (thief, troll, etc.)
  - [ ] Darkness and light mechanics (grue danger) [partially complete, revisit for full parity]
  - [ ] Endgame logic and victory conditions
- [ ] Room/location parity
  - Ensure all rooms, locations, and connections match the original Zork I map and source.
- [ ] Ensure gameplay functionality, look, and feel.

## Completed Tasks (see CHANGELOG.md for details)

- [x] Enrich all rooms with real data, exits, objects, flags, and actions
- [x] Automate exit population from source
- [x] Validate room and exit data with map comparison script
- [x] Remove stray/duplicate room/object code
- [x] Add missing imports and class definitions for Room and GameObject
- [x] Document enrichment logic and mapping for maintainers

## Reference

- For completed milestones and version history, see CHANGELOG.md
