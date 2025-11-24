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
- Expand parser to handle more tags and properties from .mud files.
- Parse and load objects from other source files.
- Implement advanced command parsing and action dispatch.
- Add save/load functionality and more gameplay features.
