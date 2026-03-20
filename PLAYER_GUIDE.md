# Phork: Player's Guide

Welcome to Phork, a faithful recreation of the classic text adventure Zork I! This guide will help you navigate the Great Underground Empire and master the art of interactive fiction.

## 🎮 Getting Started

### How to Play
1. **Start the game**: Run `python3 main.py` from the project directory
2. **Read descriptions**: The game describes your surroundings and situation
3. **Type commands**: Enter commands in natural English (e.g., "take lamp", "go north")
4. **Explore and interact**: Move between rooms, examine objects, solve puzzles
5. **Save your progress**: Use `save` and `load` commands to preserve your adventure

### Basic Game Concepts

**Rooms**: You move between different locations, each with unique descriptions, objects, and exits.

**Objects**: Items you can take, examine, use, and interact with. Some are treasures worth points!

**Inventory**: Items you're carrying. Check with `inventory` or `i`.

**Puzzles**: Challenges that require creative thinking and object manipulation.

**Score**: Points earned by finding treasures and solving puzzles. Check with `score`.

---

## 📋 Command Reference

### Movement Commands
- `north`, `south`, `east`, `west`, `up`, `down` - Move in cardinal directions
- `n`, `s`, `e`, `w`, `u`, `d` - Short forms
- `northeast`, `northwest`, `southeast`, `southwest` - Diagonal directions  
- `ne`, `nw`, `se`, `sw` - Short forms for diagonals
- `enter [object]` - Enter a building, vehicle, or container
- `exit` - Leave your current location
- `climb [object]` - Climb stairs, ladders, trees, etc.

### Observation Commands
- `look` or `l` - Look around your current location
- `look at [object]` - Examine a specific object closely  
- `examine [object]` or `x [object]` - Detailed examination
- `look in [container]` - Look inside containers, boxes, etc.
- `look under [object]` - Look under furniture, rugs, etc.
- `search [object]` - Search objects thoroughly
- `inventory` or `i` - See what you're carrying
- `score` - Check your current score and rank

### Object Manipulation
- `take [object]` or `get [object]` - Pick up an object
- `drop [object]` - Drop an object you're carrying
- `put [object] in [container]` - Place an object in a container
- `take [object] from [container]` - Remove an object from a container
- `open [object]` - Open doors, containers, etc.
- `close [object]` - Close doors, containers, etc.
- `turn on [object]` - Activate lamps, switches, etc.
- `turn off [object]` - Deactivate objects
- `light [object]` - Light torches, matches, etc.
- `extinguish [object]` - Put out fires, lights, etc.

### Bulk Actions
- `take all` - Take all visible objects in the room
- `drop all` or `drop everything` - Drop everything you're carrying  
- `take all from [container]` - Take everything from a container
- `drop all in [container]` - Put everything in a container

### Interaction Commands
- `read [object]` - Read books, papers, inscriptions
- `push [object]` - Push buttons, levers, objects
- `pull [object]` - Pull handles, ropes, objects  
- `turn [object]` - Turn knobs, wheels, keys
- `move [object]` - Try to move heavy objects
- `touch [object]` - Touch objects (sometimes reveals information)
- `use [object]` - Use tools and special items
- `wear [object]` - Put on clothing or accessories
- `remove [object]` - Take off clothing or accessories

### Communication & Help
- `help` - Display help information
- `verbose` - Switch to detailed room descriptions
- `brief` - Switch to short room descriptions
- `commands` - List available commands (this varies by context)
- `quit` or `q` - Exit the game
- `restart` - Start the game over from the beginning

### Game Management
- `save` - Save your current game progress
- `save [filename]` - Save with a specific filename
- `load` - Load your most recent save
- `load [filename]` - Load a specific save file
- `version` - Display game version information

---

## 💡 Gameplay Tips

### Essential Survival
1. **Get light first!** Find and turn on the lamp - darkness is dangerous (grues!)
2. **Map as you go** - Keep track of room connections and important items
3. **Examine everything** - Objects often have hidden properties or clues
4. **Try different phrasings** - "open door", "unlock door", "push door" might work differently

### Problem-Solving Strategies
1. **Read all text carefully** - Descriptions contain important clues
2. **Look for patterns** - Similar puzzles often have similar solutions
3. **Try obvious actions first** - Simple solutions often work
4. **Combine objects creatively** - Many puzzles require using multiple items together
5. **Save before risky actions** - Save before trying dangerous things

### Common Puzzle Types
- **Locked doors/containers**: Look for keys or other opening methods
- **Dark areas**: Find light sources (lamp, torch, matches)
- **Blocked passages**: Look for switches, levers, or objects to move
- **Complex mechanisms**: Read inscriptions and experiment carefully
- **Treasure collection**: Some treasures only count when brought to specific locations

### Command Shortcuts & Alternatives
- Most commands have multiple forms: "take" = "get", "examine" = "look at" = "x"
- Articles are optional: "take the sword" = "take sword"
- Prepositions are flexible: "put sword in case" = "place sword in case"
- The parser is forgiving - try natural language

---

## 🏆 Scoring System

### How Scoring Works
- **Treasures**: Finding and depositing valuable objects
- **Puzzle solving**: Overcoming major challenges
- **Exploration**: Discovering new areas
- **Survival**: Avoiding death and dangerous situations

### Treasure Values
Different treasures are worth different points. Some examples:
- **Common items**: 2-5 points
- **Valuable treasures**: 10-15 points  
- **Legendary artifacts**: 15+ points

### Ranking System
Your score determines your adventuring rank:
- **Beginner**: 0-100 points
- **Novice**: 100-200 points
- **Competent**: 200-300 points
- **Expert**: 300+ points
- **Master**: Maximum score

---

## ⚠️ Important Warnings

### Deadly Situations
- **Darkness without light**: The grues will get you!
- **Dangerous areas**: Some rooms have environmental hazards
- **Poor decisions**: Some actions can end your adventure permanently

### Game-Ending Scenarios
- **Death**: You can die from various causes (restart or load to continue)
- **Impossible states**: Rare situations where puzzles become unsolvable
- **Resource depletion**: Running out of essential items

### Recovery Options
- **Save frequently** - Before entering new areas or attempting risky actions
- **Multiple saves** - Keep several save files for different progress points
- **Restart if needed** - Sometimes starting over with new knowledge is fastest

---

## 🎯 Quick Start Walkthrough

### Your First Steps
1. **Start the game** - You'll be standing outside a house
2. **Go around** - `go south` then `east` to find the kitchen door
3. **Enter the house** - `open door`, then `enter house` 
4. **Get the lamp** - `take lamp` (essential for survival!)
5. **Turn on light** - `turn on lamp` (before going anywhere dark)
6. **Explore safely** - Now you can venture into darker areas

### Early Game Objectives
- Find and secure a light source
- Explore the house and immediate surroundings
- Collect easily accessible treasures
- Learn the basic game mechanics through experimentation

---

## 🆘 Troubleshooting

### "I Don't Understand" Messages
- Try simpler phrasing: "use sword" instead of "attack with sword"
- Use different verbs: "push", "pull", "turn", "move"
- Check spelling and try synonyms
- Make sure you can see the object you're trying to use

### "You Can't Do That" Messages  
- You might not have required items or prerequisites
- Location might matter - try the same action elsewhere
- Object state might be wrong (locked, closed, etc.)
- Try examining the object for clues about what's possible

### Lost or Stuck?
- Use `look` to re-read your current location
- Try `inventory` to see what tools you have available
- Examine everything in your current location
- Consider retracing your steps or trying a different approach
- Save and experiment - you can always reload

---

**Remember**: Text adventures reward curiosity, experimentation, and creative thinking. Don't be afraid to try unusual commands or combinations - you might discover something unexpected!

**Good luck, adventurer!** The Great Underground Empire awaits your exploration. 🗡️✨