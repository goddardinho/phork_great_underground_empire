# FEATURE: Canonical NPCs Implementation

**Branch**: `feature/canonical-npcs`  
**Started**: 2026-03-23  
**Base Version**: v1.4.0  
**Target Version**: v1.5.0  

## 🎯 **Objective**

Implement all canonical Non-Player Characters from original Zork I with authentic behaviors, interactions, and game mechanics.

## 📋 **Scope**

### **Canonical NPCs to Implement**
- [ ] **Thief** - Steals objects, can be fought, drops loot when defeated
- [ ] **Troll** - Guards bridge, requires payment or combat to pass
- [ ] **Cyclops** - Ancient creature with specific interaction patterns
- [ ] **Master** - Endgame character with complex dialogue
- [ ] **Woodsman** - Forest character with helpful information
- [ ] **Sailor** - Harbor character with sea-related lore

### **Combat System**
- [ ] Basic attack/defend mechanics
- [ ] Health/damage system for NPCs and player
- [ ] Weapon effectiveness and combat calculations
- [ ] Death and respawn mechanics
- [ ] Combat feedback and descriptions

### **Advanced NPC Behaviors**
- [ ] NPC movement between rooms
- [ ] Object stealing and inventory management
- [ ] Conditional responses based on game state
- [ ] NPC-to-NPC interactions
- [ ] Time-based behaviors and events

### **Integration & Polish**
- [ ] Update existing room descriptions with NPC presence
- [ ] Canonical placement of NPCs in correct rooms
- [ ] Proper NPC state persistence in save/load system
- [ ] Integration with existing puzzle and scoring systems

## 🏗️ **Technical Architecture**

### **Existing Foundation** (v1.4.0)
✅ NPC entity system (NPC, DialogueNode, DialogueResponse)  
✅ NPCManager for centralized state management  
✅ Basic conversation commands (talk, ask, greet, say)  
✅ Debug system integration (`debug npc`)  

### **Phase 1 Complete** (v1.5.0-dev)
✅ **Combat System** - Complete CombatManager with fight mechanics, health, damage, weapons  
✅ **Combat Integration** - All existing NPCs have full combat stats and capabilities  
✅ **Combat Commands** - attack, defend, flee commands with proper game integration  
✅ **Debug & Testing** - Combat debug system and comprehensive test suite  

### **Current NPCs Status**
✅ **Test NPCs** - Hermit (simple) and Oracle (complex dialogue) in West of House  
✅ **Combat Ready** - Both NPCs fully integrated with combat system  
❌ **Canonical NPCs** - None implemented yet (Thief, Troll, Cyclops, Master, Woodsman, Sailor)  

### **New Components Still Needed**
- [ ] **NPC AI** - MovementManager for NPC pathfinding and behaviors
- [ ] **Advanced Dialogue** - Conditional dialogue trees and state-dependent responses
- [ ] **Inventory Management** - NPC object handling and theft mechanics
- [ ] **Event System** - Time-based and trigger-based NPC events

## 📝 **Implementation Plan**

### **Phase 1: Combat Foundation**
- [x] Design combat mechanics (health, weapons, damage)
- [x] Implement CombatManager class
- [x] Add combat commands (attack, defend, flee)
- [x] Create basic combat testing framework

### **Phase 2: Thief Implementation**
- [ ] Create Thief NPC with theft behaviors
- [ ] Implement object stealing mechanics
- [ ] Add Thief combat interactions
- [ ] Test Thief integration with existing systems

### **Phase 3: Troll & Bridge Puzzle**
- [ ] Implement Troll NPC with bridge guarding behavior
- [ ] Create payment/toll mechanics
- [ ] Add Troll combat as alternative to payment
- [ ] Integrate with bridge traversal puzzle

### **Phase 4: Additional Canonical NPCs**
- [ ] Cyclops with ancient creature behaviors
- [ ] Master with endgame dialogue complexity
- [ ] Woodsman with helpful forest information
- [ ] Sailor with maritime lore and interactions

### **Phase 5: Advanced Features**
- [ ] NPC movement and pathfinding
- [ ] Complex NPC-to-NPC interactions
- [ ] Time-based events and behaviors
- [ ] State-dependent dialogue and responses

### **Phase 6: Integration & Testing**
- [ ] Update all room descriptions with NPC presence
- [ ] Comprehensive testing of all NPC interactions
- [ ] Save/load system integration for NPC states
- [ ] Performance testing with multiple active NPCs
- [ ] Debug system enhancement for combat testing

## 🧪 **Testing Strategy**

- [x] **Unit Tests**: Individual NPC behavior testing ✅ **COMPLETE** (test_combat_system.py)
- [x] **Combat Tests**: Fight mechanics and damage calculations ✅ **COMPLETE** (6 passing tests)
- [x] **Integration Tests**: NPC interactions with existing systems ✅ **COMPLETE** (combat integration validated)
- [x] **Live Testing**: Real gameplay validation ✅ **COMPLETE** (attack/defend/flee commands working)
- [ ] **Canonical NPC Tests**: Thief theft mechanics, Troll bridge guarding, etc.
- [ ] **Performance Tests**: Multiple NPCs active simultaneously
- [ ] **Save/Load Tests**: NPC state persistence validation
- [ ] **Gameplay Tests**: Full canonical scenario validation
- [ ] **Performance Tests**: Multiple NPCs active simultaneously
- [ ] **Save/Load Tests**: NPC state persistence validation

## 🎮 **Success Criteria**

### **Phase 1 Achievements** ✅ **COMPLETE**
- [x] Complete combat system with weapon effectiveness
- [x] Perfect integration with existing conversation system  
- [x] Comprehensive test coverage for combat systems
- [x] Debug system supports full NPC/combat testing
- [x] All existing NPCs (Hermit, Oracle) combat-ready

### **Remaining Goals**
- [ ] All 6+ canonical NPCs implemented with authentic behaviors
- [ ] NPC movement and advanced AI behaviors working
- [ ] All NPC interactions match original Zork specifications
- [ ] Documentation updated with complete NPC usage guide
- [ ] Save/load integration for all NPC states

## 📚 **References**

- Original Zork I source code (zork_mtl_source/)
- Existing NPC conversation system (v1.4.0)
- Combat mechanics from original game documentation
- NPC placement and behavior specifications

---

**Current Status**: Phase 1 (Combat Foundation) and Phase 2 (Thief NPC) are complete. Phase 3 (Troll NPC) is ready to begin.