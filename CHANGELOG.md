# Changelog

## v0.2.7 (2025-12-02)

- Added canonical support for missing Zork I actions: 'put <item> in <container>', 'place <item> on <surface>', 'unlock <container> with <key>', 'lock <container>', 'tie <object> to <object>', 'turn <object>', and expanded 'search' for containers/rooms.
- Implemented snarky/canonical responses for unsupported or invalid targets (e.g., placing objects on NPCs, using non-surface objects).
- All new actions validated for canonical feedback and gameplay parity.
- Updated command parser and game logic to match Zork I source behavior for object/NPC interactions and feedback.

## v0.2.6 (2025-12-02)

- Canonical Zork I death and restart logic implemented: player death triggers canonical message and offers restart, restore, or quit options.
- Game restart resets all state; restore loads a saved game; quit exits cleanly.
- Save/load system expanded to persist and restore full game state, including player, inventory, rooms, NPCs, puzzles, flags, thief state, demo mode, and all mutable attributes.
- All gameplay progress, health, and world state are now fully preserved and restored.
- Ready for robust in-game testing and further feature development.

## v0.2.5 (2025-12-02)

- Canonical NPCs (Thief, Troll, Cyclops, Grue, Robot) fully implemented with all source-accurate interactions and behaviors.
- Modular two-way combat system added (`combat.py`), supporting multi-round combat, wounds, stagger, and death for both player and NPCs.
- NPC classes updated with canonical weapon and attack descriptions (e.g., Troll's bloody axe, Thief's stiletto, Cyclops' fists/throwing).
- Command parser refactored to route all combat and interaction commands to modular logic.
- Thief random encounter logic implemented: random movement, appearance, and canonical actions.
- Source code scanned and validated for all canonical NPCs; no missing NPCs found.
- All changes validated for source parity and canonical Zork I behavior.

## v0.2.3 (2025-11-26)

- Puzzle and treasure scoring system fully implemented and tested.
- Multi-step puzzle/event framework added with registry and stateful handlers.
- All canonical Zork I puzzles, treasures, and events now award correct score values.
- Automated tests for puzzle triggers and scoring pass for all supported features.
- TODO.md and README.md updated to mark puzzle scoring and multi-step event logic as complete.

## v0.2.0 (2025-11-25)

- Game engine refactored for feature parity with original Zork I source.
- Parser expanded to support all canonical Zork I commands and synonyms.
- Object interaction logic implemented (get, drop, examine, open, close, etc.).
- Room flags and puzzle support stubbed and integrated.
- Save/load functionality added using pickle for game state persistence.
- All roadmap items for v0.2.0 marked complete in README.md and TODO.md.
- Inventory weight tracking and canonical carry limit implemented (OSIZE, LOAD_MAX).
- 'Take all' and 'drop all' commands added.
- Demo mode for testing all objects and disabling carry limits.
- Darkness and grue mechanics implemented: warning on first move/action in darkness, grue death on second, matches canonical Zork I behavior.
- TODO.md and README.md updated for gameplay parity tracking and completed features.
- Deduplicated TODO.md for clarity.

## v0.1.9 (2025-11-24)

- Automated population of room exits in `main.py` using parsed MUD source data.
- Validated all room and exit data with a Python-to-source map comparison script; no mismatches found.
- Removed all stray and duplicate room/object code, ensuring a clean and error-free codebase.
- Added missing imports and minimal class definitions for `Room` and `GameObject` to support robust parsing and comparison.
- All enrichment and exit extraction tasks are now fully automated and validated.

## v0.1.8 (2025-11-24)

- Completed enrichment and validation of all rooms, including ALICE-ROOM, CYCLOPS-WEST-ROOM, CYCLOPS-UP-STAIRS, and THIEF-ROOM, using inferred context and game logic.
- All rooms now have detailed descriptions, exits, objects, flags, and actions for gameplay fidelity.
- Updated TODO.md to mark all enrichment and validation tasks as complete.
- Ready for gameplay testing and further feature development.

## v0.1.7 (2025-11-24)

- Deduplicated all room definitions in `main.py`, keeping only the most enriched version for each room.
- Enriched rooms with missing objects, exits, flags, and actions based on original MUD source.
- Clarified and improved room descriptions for gameplay fidelity.
- Added conditional exits and objects to rooms where appropriate.
- Removed minimal and duplicate room entries.
- Prepared room data for further enrichment and gameplay logic.

## v0.1.6 (2025-11-21)

- Added map visualization script using networkx and matplotlib (visualize_map.py).
- Installed required Python packages and set up project virtual environment.
- Created .gitignore for Python, VS Code, OS, and output files.
- Successfully displayed Zork map graph with room nodes and labeled exits.

## v0.1.5 (2025-11-21)

- Updated map generation logic to scan all .mud files for <DEFINE ROOMNAME ...> blocks and multi-line exit references.
- Parser now extracts rooms and exits using <GOTO>, <SFIND-ROOM>, <REXITS>, and related tags, handling indirect and multi-line definitions.
- map.json now contains a large set of room nodes and edges, representing the game world graph.
- Improved extraction logic for more robust gameplay duplication and future visualization.

## v0.1.4 (2025-11-21)

- Integrated object loading from .mud files using the generic parser.
- Refined type handling for Room and GameObject classes with Optional and type annotations.
- Improved code structure for future extensibility and error handling.

## v0.1.3 (2025-11-21)

- Added generic .mud file parser to extract tags and properties from any .mud file.
- Parser supports flexible tag extraction for objects, actions, flags, and more.
- Ready for integration with game data loading and expansion.

# Changelog

## v0.1.2 (2025-11-21)

- Further expanded rooms.mud parser to extract flags (<FLAGWORD>) and actions (<RACTION>).
- Parser now supports additional room properties and is ready for future extensibility.
- Improved object parsing to allow for future attributes.

## v0.1.1 (2025-11-21)

- Expanded rooms.mud parser to extract exits and objects using regex.
- Added support for parsing <EXIT> and <OBJ> tags in room definitions.
- Parser structure ready for adaptation to other .mud files.

## v0.1.0 (2025-11-21)

- Project initialized: basic repo structure and source scan.
- Implemented core data structures: Room, GameObject, Player, Action.
- Created main game loop and basic parser for player input.
- Added dynamic room loader using Python structure.
- Implemented basic parser for rooms.mud to extract room names and descriptions.

## Planned/Next Steps

- See the Roadmap section in README.md for all planned and future features.

> For current development focus, see TODO.md
