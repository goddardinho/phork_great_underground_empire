# Save/Load Edge Case Test Scenarios

This document lists key scenarios to test for robust, source-faithful save/load functionality in the Phork project.

## Edge Case Scenarios

1. **Save and load during an unsolved puzzle**
   - Test saving and restoring with a puzzle in progress or partially completed.
2. **Save and load in a dark room**
   - Player is in darkness; verify grue danger and darkness counter are preserved.
3. **Save and load with NPCs present**
   - Thief, troll, or cyclops is in the same room as the player.
4. **Save and load after player death(s)**
   - Test after one or multiple deaths; verify death counter and respawn logic.
5. **Save and load with objects in containers**
   - Items are inside containers (e.g., mailbox, treasure chest).
6. **Save and load with lantern state**
   - Lantern is lit/unlit and in different locations (inventory, room, container).
7. **Save and load after a random event**
   - E.g., thief steals an item, NPC moves, or other random event occurs.
8. **Save and load in demo mode**
   - Test inventory, NPCs, and carry limits in demo mode.
9. **Save and load at endgame or restricted state**
   - Attempt to save/load in endgame or other restricted states; should be blocked or handled gracefully.
10. **Save and load with corrupted or missing save file**
    - Test error handling for file issues.

## Optional (for absolute parity)
- Save/load with active timers or countdowns (if implemented)
- Save/load with partially completed multi-step puzzles
- Save/load with all possible room/flag/NPC combinations

---

Use this list to guide automated and manual testing for robust, Zork-faithful save/load support.
