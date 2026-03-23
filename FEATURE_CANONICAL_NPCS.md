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

### **New Components Needed**
- [ ] **Combat System** - CombatManager class for fight mechanics
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

- [ ] **Unit Tests**: Individual NPC behavior testing
- [ ] **Combat Tests**: Fight mechanics and damage calculations  
- [ ] **Integration Tests**: NPC interactions with existing systems
- [ ] **Gameplay Tests**: Full canonical scenario validation
- [ ] **Performance Tests**: Multiple NPCs active simultaneously
- [ ] **Save/Load Tests**: NPC state persistence validation

## 🎮 **Success Criteria**

- [ ] All 6+ canonical NPCs implemented with authentic behaviors
- [ ] Complete combat system with weapon effectiveness
- [ ] NPC movement and advanced AI behaviors working
- [ ] Perfect integration with existing conversation system
- [ ] All NPC interactions match original Zork specifications
- [ ] Comprehensive test coverage for all NPC systems
- [ ] Debug system supports full NPC/combat testing
- [ ] Documentation updated with NPC usage guide

## 📚 **References**

- Original Zork I source code (zork_mtl_source/)
- Existing NPC conversation system (v1.4.0)
- Combat mechanics from original game documentation
- NPC placement and behavior specifications

---

**Next Steps**: Begin with Phase 1 - Combat Foundation implementation.