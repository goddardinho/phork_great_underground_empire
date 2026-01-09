# Phork: A Text-Based Adventure Game

Phork is a clean-room Python reimplementation of the classic Zork I, inspired by the original MDL source code. This project aims for feature parity and map fidelity with Zork I, using only the original source files in `zork_mtl_source` as reference.

## Features

- Text-based interactive fiction gameplay
- Room and object structure based on Zork I
- Modular, extensible Python codebase
- MIT License

## Getting Started

1. Clone this repository.
2. Ensure you have Python 3.8+ installed.
3. Run the game:
   ```sh
   python main.py
   ```

## Project Structure

- `main.py` — Main game loop and logic
- `zork_mtl_source/` — Original Zork I MDL source files (reference only)
- `.gitignore` — Standard Python and project ignores

## Roadmap

- [x] Extract and implement all rooms and connections from `rooms.mud`
- [x] Expand parser to handle more tags and properties from .mud files
- [x] Parse and load objects from other source files
- [x] Implement advanced command parsing and action dispatch
- [x] Expand parser to support all Zork I commands
- [x] Implement puzzles, NPCs, and advanced object logic
- [x] Add automated tests for movement, puzzles, and map fidelity
- [x] Add save/load functionality and more gameplay features
- [ ] Room/location parity
- [ ] Gameplay parity

## License

MIT License. See LICENSE file for details.

## Credits

- Inspired by Zork I (Infocom, MIT DM Group)
- Original MDL source: [historicalsource/zork](https://github.com/historicalsource/zork)
- GitHub Copilot for doing the majority of the work!
