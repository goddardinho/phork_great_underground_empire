# Phork Rewrite - Development Roadmap

*🔄 This project has been completely rewritten with a clean, modular architecture. Previous implementation is preserved in `backup/pre-rewrite` branch.*

## Immediate Priorities (v1.0 Foundation)

### Core Gameplay Loop
- [x] Basic movement system (north, south, east, west, up, down)
- [x] Look and examine commands  
- [x] Basic inventory management (take, drop, inventory)
- [x] Simple command parser with synonyms
- [ ] **Robust object interaction** (open, close, read, etc.)
- [ ] **Container support** (put X in Y, get X from Y)  
- [ ] **Multiple object names and aliases**

### World Building  
- [x] Room system with exits and descriptions
- [x] Basic object placement in rooms
- [ ] **Load rooms from original .mud files** (data/ directory)
- [ ] **Dynamic room descriptions** (visited/unvisited states)
- [ ] **Room flags** (dark, dangerous, etc.)

### Parser Enhancement
- [x] Basic verb-noun parsing
- [ ] **Preposition handling** (put X in Y, look at X, etc.)
- [ ] **Ambiguity resolution** (which sword - the rusty one or the silver one?)
- [ ] **Synonym expansion** from Zork vocabulary

## Medium-term Goals (v1.1 - Zork Parity)

### Objects & Puzzles  
- [ ] Container objects (mailbox, chest, etc.)
- [ ] Light sources and darkness mechanics
- [ ] Multi-step puzzles 
- [ ] Score system
- [ ] Object combinations and transformations

### NPCs & Combat
- [ ] Basic NPC conversations
- [ ] Thief, Troll, and other iconic characters  
- [ ] Simple combat system
- [ ] NPC movement and behaviors

### Game State
- [ ] Save/load functionality
- [ ] Death and restart mechanics  
- [ ] Inventory size limits and object weight
- [ ] Time-based events

## Long-term Vision (v2.0+)

### Enhanced Features
- [ ] Rich text descriptions and formatting
- [ ] Sound effects and multimedia (optional)
- [ ] Hint system
- [ ] Multiple difficulty levels
- [ ] Procedural content expansion

### Technical Improvements  
- [ ] Performance optimization for large worlds
- [ ] Plugin system for custom content
- [ ] Web interface option
- [ ] Multi-language support

## Development Standards

- **Type Safety**: All new code must have complete type hints
- **Testing**: Unit tests for all new functionality
- **Documentation**: Docstrings for all public interfaces  
- **Code Quality**: Black formatting, mypy type checking

## Note on Original Implementation

The previous complex implementation with 20+ modules has been archived. While feature-rich, it had become difficult to maintain due to circular dependencies and unclear separation of concerns. This rewrite prioritizes:

1. **Simplicity** over feature completeness initially
2. **Architecture** that can grow without becoming unwieldy  
3. **Test coverage** from the beginning
4. **Clear interfaces** between components

The goal is to rebuild functionality systematically on a foundation that will support long-term growth and maintenance.

## Reference

- For completed milestones and version history, see CHANGELOG.md
