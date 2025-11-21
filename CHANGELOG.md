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
