# Phork: A Text-Based Adventure Game

Phork is a clean-room Python reimplementation of the classic Zork I, inspired by the original MDL source code. This project aims for feature parity and map fidelity with Zork I, using only the original source files in `zork_mtl_source` as reference.

**🔄 Recently Rewritten** - This project has been completely rewritten from the ground up with a clean, modular architecture for better maintainability and extensibility.

## Features

- Text-based interactive fiction gameplay
- Clean, modular Python architecture with full type hints
- Room and object structure based on Zork I
- Extensible command parser with natural language processing
- **Intelligent ambiguity resolution** - handles "which sword - the rusty one or the silver one?"
- Dynamic room descriptions with brief/verbose modes
- Room flags system (light sources, dangers, atmospheric effects)
- Container support with nested object interactions
- Comprehensive test suite for reliability
- MIT License

## Getting Started

### Quick Start
```bash
# Setup (first time only)
./setup.sh

# Activate environment and run
source .venv/bin/activate
PYTHONPATH=. python main.py
```

### Manual Setup
1. Clone this repository
2. Ensure you have Python 3.8+ installed
3. Create virtual environment: `python -m venv .venv`
4. Activate environment: `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Run the game: `PYTHONPATH=. python main.py`

## Architecture

This rewrite focuses on:
- **Clean separation of concerns** - Each module has a single responsibility
- **Type safety** - Full type hints throughout codebase
- **Testability** - Easy to unit test each component
- **Maintainability** - Clear, readable code structure

### Project Structure

```
src/
├── game.py              # Main game engine and coordination
├── world/               # Game world (rooms, connections)
│   ├── room.py          # Room class and logic
│   └── world.py         # World container and management
├── entities/            # Game objects and characters
│   ├── player.py        # Player state and inventory
│   └── objects.py       # Game items and their behaviors
├── parser/              # Command parsing and interpretation
│   └── command_parser.py # Natural language command processing
└── utils/               # Utility functions and loaders
tests/                   # Comprehensive test suite
zork_mtl_source/        # Original Zork I MDL source files (reference)
```

## Development

```bash
# Run tests
python -m pytest tests/

# Type checking (when mypy is installed)
mypy src/

# Code formatting (when black is installed) 
black src/ tests/
```

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
