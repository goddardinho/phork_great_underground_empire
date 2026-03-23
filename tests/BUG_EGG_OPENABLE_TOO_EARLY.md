# BUG: Jewel-Encrusted Egg Can Be Opened Too Early

## Description
The jewel-encrusted egg is currently openable immediately after being collected from the nest. In canonical Zork, the egg should not be openable until the player has progressed further (typically after acquiring a specific item or reaching a certain location/event).

## Steps to Reproduce
1. Go to the tree and examine the nest.
2. Take the jewel-encrusted egg.
3. Attempt to open the egg.

**Observed:** The egg opens and is empty.
**Expected:** The egg should not be openable until a later point in the game (e.g., after a puzzle or with a special item).

## Impact
- Breaks canonical puzzle sequence and progression.
- Allows players to bypass intended challenge.

## Suggested Fix
- Add a lock or condition to the egg so it cannot be opened until the correct event or item is used.
- Update object state and interaction logic accordingly.

---
Created automatically by GitHub Copilot on 2026-03-23.
