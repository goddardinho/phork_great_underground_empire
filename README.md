# Phork: A Text-Based Adventure Game

Phork is a clean-room Python reimplementation of the classic Zork I, inspired by the original MDL source code. This project aims for feature parity and map fidelity with Zork I, using only the original source files in `zork_mtl_source` as reference.

**🎉 v1.2.2 Enhanced!** - **ObjectManager Architecture & Canonical Descriptions** - Major architectural improvements with modular object management and authentic room descriptions.

## Features

- Text-based interactive fiction gameplay
- **Modular ObjectManager architecture** - Clean separation of object management and game logic
- **Canonical room descriptions** - Authentic descriptions for iconic rooms (Behind House window, Kitchen, Living Room)
- Room and object structure based on Zork I with canonical accuracy
- Extensible command parser with natural language processing
- **Robust disambiguation system** - Graceful handling of ambiguous commands and edge cases
- Dynamic room descriptions with brief/verbose modes
- Room flags system (light sources, dangers, atmospheric effects)
- Container support with nested object interactions
- **Comprehensive test suite** - All core tests passing with improved compatibility
- **Security hardened** - Path traversal prevention, input validation, secure error handling
- MIT License

## Getting Started

### Quick Start
```bash
# Setup (first time only)
./setup.sh

# Activate environment and play full Zork
source .venv/bin/activate
python3 main.py
```

### Development Mode
```bash
# Use simple test world for development
python3 main.py --test

# Enable debug mode with detailed information
python3 main.py --debug

# Run disambiguation demo
python3 main.py --demo-disambiguation
```

### Debug Mode Features
When running with `--debug`, additional commands become available:
- `debug npc` - Comprehensive NPC system testing and interaction
- `debug menu` - Show all available debug commands  
- `debug world` - Display world and room information
- `debug objects` - Show object system details

### New to Text Adventures?
📖 **[Read the Player's Guide](PLAYER_GUIDE.md)** for complete gameplay instructions, command reference, tips, and strategies.

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
└── parsers/             # Specialized file format parsers
    └── mdl_parser.py   # Original .mud file parser
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

## 🚀 **Automated Development Workflow**

This project includes automation tools for streamlined development:

### **Quick Commands**
```bash
# Create new feature branch with documentation template
./scripts/new-feature.sh security-validation

# Interactive version tagging with changelog validation  
./scripts/create-version.sh
```

### **Automatic Features**
- ✅ **Auto-push tags**: Tags automatically push with commits
- ✅ **Documentation checks**: Pre-push hook validates CHANGELOG.md updates
- ✅ **Version suggestions**: Smart version number recommendations
- ✅ **Feature planning**: Auto-generated planning templates

📖 **Full workflow guide**: See [WORKFLOW.md](WORKFLOW.md)

## Documentation

### For Players
- 📖 **[Player's Guide](PLAYER_GUIDE.md)** - Complete gameplay instructions and command reference

### For Developers  
- 🛠️ **[Coding Standards](CODING_STANDARDS.md)** - Development conventions and best practices
- 🔒 **[Security Report](SECURITY_REPORT.md)** - Comprehensive security assessment and measures
- 📋 **[Workflow Guide](WORKFLOW.md)** - Automated development workflow and tools

### Coverage & Quality
- 🧪 **Test Coverage**: HTML coverage report available in `htmlcov/index.html`
- 🔍 **Static Analysis**: Security scanning with Bandit, dependency checks with Safety

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
