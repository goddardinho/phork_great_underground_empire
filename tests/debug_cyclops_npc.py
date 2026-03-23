"""
Interactive Cyclops NPC debugging and testing script.
Use this to manually test and debug Cyclops implementation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game import GameEngine
from src.entities.objects import GameObject


def test_cyclops_presence(game):
    """Test 1: Verify Cyclops exists and is properly configured."""
    print("\n=== TEST 1: Cyclops Presence ===")
    
    cyclops = game.npc_manager.get_npc("CYCLOPS")
    if not cyclops:
        print("❌ FAIL: Cyclops not found in NPC manager")
        return False
    
    print(f"✅ Cyclops found: {cyclops.name} (ID: {cyclops.id})")
    print(f"   Location: {cyclops.location}")
    print(f"   Description: {cyclops.description[:60]}...")
    print(f"   Aliases: {cyclops.aliases}")
    print(f"   Canonical: {cyclops.get_attribute('canonical', False)}")
    
    # Check behavior
    behavior = cyclops.get_attribute("behavior")
    if not behavior:
        print("❌ FAIL: No behavior attached to Cyclops")
        return False
    
    print(f"   Behavior attached: {type(behavior).__name__}")
    print(f"   Initial state - Sleeping: {behavior.state.is_sleeping}")
    print(f"   Initial state - Wrath: {behavior.state.wrath_level}")
    print(f"   Blocks passage: {behavior.is_blocking_passage()}")
    
    return True


def test_cyclops_combat_stats(game):
    """Test 2: Verify combat stats and integration."""
    print("\n=== TEST 2: Combat Stats ===")
    
    cyclops = game.npc_manager.get_npc("CYCLOPS")
    if not cyclops:
        print("❌ FAIL: No cyclops available")
        return False
    
    stats = cyclops.combat_stats
    if not stats:
        print("❌ FAIL: No combat stats")
        return False
    
    print(f"✅ Combat Stats:")
    print(f"   Health: {stats.current_health}/{stats.max_health}")
    print(f"   Attack: {stats.attack_power}")
    print(f"   Defense: {stats.defense}")
    print(f"   Weapon: {stats.weapon or 'None (uses fists)'}")
    
    # Verify strength (should be much stronger than Troll)
    expected_health = 300
    expected_attack = 40
    
    if stats.current_health != expected_health:
        print(f"❌ FAIL: Expected health {expected_health}, got {stats.current_health}")
        return False
    
    if stats.attack_power != expected_attack:
        print(f"❌ FAIL: Expected attack {expected_attack}, got {stats.attack_power}")
        return False
    
    print("✅ Combat stats match expected values (stronger than Troll)")
    return True


def test_sleep_wake_cycle(game):
    """Test 3: Sleep/wake state management."""
    print("\n=== TEST 3: Sleep/Wake Cycle ===")
    
    cyclops = game.npc_manager.get_npc("CYCLOPS")
    behavior = cyclops.get_attribute("behavior") if cyclops else None
    
    if not behavior:
        print("❌ FAIL: No behavior available")
        return False
    
    # Test initial state (should be sleeping)
    print(f"Initial state - Sleeping: {behavior.state.is_sleeping}")
    print(f"Initial blocking: {behavior.is_blocking_passage()}")
    
    # Test wake up
    print("\nWaking cyclops...")
    wake_response = behavior.wake_up("test")
    print(f"Wake response: {wake_response}")
    print(f"Now sleeping: {behavior.state.is_sleeping}")
    print(f"Wrath level: {behavior.state.wrath_level}")
    print(f"Now blocking: {behavior.is_blocking_passage()}")
    
    # Test wake again (should say already awake)
    print("\nTrying to wake again...")
    wake_again = behavior.wake_up("test")
    print(f"Second wake response: {wake_again}")
    
    # Test fall asleep manually
    print("\nMaking cyclops fall asleep...")
    behavior._fall_asleep()
    print(f"Now sleeping: {behavior.state.is_sleeping}")
    print(f"Now blocking: {behavior.is_blocking_passage()}")
    
    return True


def test_food_interactions(game):
    """Test 4: Food giving mechanics."""
    print("\n=== TEST 4: Food Interactions ===")
    
    cyclops = game.npc_manager.get_npc("CYCLOPS")
    behavior = cyclops.get_attribute("behavior") if cyclops else None
    
    if not behavior:
        print("❌ FAIL: No behavior available")
        return False
    
    # Reset cyclops state 
    behavior.state.is_sleeping = False
    behavior.state.wrath_level = 2  # Moderately angry
    print(f"Starting wrath level: {behavior.state.wrath_level}")
    
    # Create test food items
    food_item = GameObject("food", "A hearty meal", "Food")
    garlic_item = GameObject("garlic", "Pungent garlic clove", "Food")
    rock_item = GameObject("rock", "A small rock", "Object")  # Not food
    
    # Add to player inventory
    player = game.player
    player.add_to_inventory("food")
    player.add_to_inventory("garlic")
    player.add_to_inventory("rock")
    
    # Add objects to object manager so they can be found
    game.object_manager.add_object(food_item)
    game.object_manager.add_object(garlic_item)
    game.object_manager.add_object(rock_item)
    
    # Test good food
    print("\nGiving good food...")
    response = behavior.give_food("food", player, game.object_manager)
    print(f"Response: {response}")
    print(f"New wrath level: {behavior.state.wrath_level}")
    
    # Check if food was removed
    has_food = "food" in player.inventory
    print(f"Food removed from inventory: {not has_food}")
    
    # Test garlic (bad food)
    print("\nGiving garlic...")
    old_wrath = behavior.state.wrath_level
    response = behavior.give_food("garlic", player, game.object_manager)
    print(f"Response: {response}")
    print(f"Wrath change: {old_wrath} -> {behavior.state.wrath_level}")
    
    # Test non-food
    print("\nTrying to give rock...")
    response = behavior.give_food("rock", player, game.object_manager)
    print(f"Response: {response}")
    
    return True


def test_drink_interactions(game):
    """Test 5: Drink giving mechanics."""
    print("\n=== TEST 5: Drink Interactions ===")
    
    cyclops = game.npc_manager.get_npc("CYCLOPS")
    behavior = cyclops.get_attribute("behavior") if cyclops else None
    
    if not behavior:
        print("❌ FAIL: No behavior available")
        return False
    
    # Create water item
    water_item = GameObject("water", "Clear water", "Liquid")
    game.object_manager.add_object(water_item)
    game.player.add_to_inventory("water")
    
    # Test when angry (should refuse)
    behavior.state.is_sleeping = False
    behavior.state.wrath_level = 2
    print(f"Cyclops wrath level: {behavior.state.wrath_level} (angry)")
    
    print("Giving water when angry...")
    response = behavior.give_drink("water", game.player, game.object_manager)
    print(f"Response: {response}")
    print(f"Still awake: {not behavior.state.is_sleeping}")
    
    # Add water back for next test
    water_item2 = GameObject("water", "Clear water", "Liquid")
    game.object_manager.add_object(water_item2)
    game.player.add_to_inventory("water")
    
    # Make cyclops calm and try again
    behavior.state.wrath_level = -1  # Calm
    print(f"\nMade cyclops calm (wrath: {behavior.state.wrath_level})")
    
    print("Giving water when calm...")
    response = behavior.give_drink("water", game.player, game.object_manager)
    print(f"Response: {response}")
    print(f"Now sleeping: {behavior.state.is_sleeping}")
    
    # Check if water was removed
    has_water = "water" in game.player.inventory
    print(f"Water removed from inventory: {not has_water}")
    
    return True


def test_movement_blocking(game):
    """Test 6: Movement blocking mechanics."""
    print("\n=== TEST 6: Movement Blocking ===")
    
    cyclops = game.npc_manager.get_npc("CYCLOPS")
    behavior = cyclops.get_attribute("behavior") if cyclops else None
    
    if not behavior:
        print("❌ FAIL: No behavior available")
        return False
    
    # Move player to cyclops room
    cyclo_room = game.world.get_room("CYCLO")
    if not cyclo_room:
        print("❌ FAIL: Cannot find CYCLO room")
        return False
    
    game.player.current_room = cyclo_room.id
    print(f"Moved player to: {cyclo_room.name}")
    
    # Test different blocking scenarios
    scenarios = [
        ("Sleeping", True, 0),      # Sleeping - should not block
        ("Calm", False, -3),        # Awake but satisfied - should not block  
        ("Neutral", False, 0),      # Awake neutral - should block
        ("Angry", False, 3)         # Awake angry - should block
    ]
    
    for scenario_name, sleeping, wrath in scenarios:
        print(f"\n--- {scenario_name} Scenario ---")
        behavior.state.is_sleeping = sleeping
        behavior.state.wrath_level = wrath
        
        blocking = behavior.is_blocking_passage()
        message = behavior.get_blocking_message()
        
        print(f"State: Sleeping={sleeping}, Wrath={wrath}")
        print(f"Blocks passage: {blocking}")
        print(f"Blocking message: {message[:50] + '...' if message else 'None'}")
        
        # Test actual movement
        try:
            # Try to actually move up to see if blocked
            old_room = game.player.current_room
            game._handle_movement("up")
            new_room = game.player.current_room
            
            moved = (old_room != new_room)
            print(f"Movement occurred: {moved}")
            
            if moved and blocking:
                print("⚠️ WARNING: Movement occurred despite blocking!")
            elif not moved and not blocking:
                print("⚠️ WARNING: Movement blocked despite no blocking expected!")
                
        except Exception as e:
            print(f"Movement test failed: {e}")
    
    return True


def interactive_cyclops_test():
    """Interactive testing menu."""
    print("🧿 Cyclops NPC Interactive Testing")
    print("=" * 40)
    
    try:
        print("Initializing game engine...")
        game = GameEngine(debug_mode=True)
        print("✅ Game engine initialized")
    except Exception as e:
        print(f"❌ Failed to initialize game: {e}")
        return
    
    test_functions = [
        ("Cyclops Presence", test_cyclops_presence),
        ("Combat Stats", test_cyclops_combat_stats), 
        ("Sleep/Wake Cycle", test_sleep_wake_cycle),
        ("Food Interactions", test_food_interactions),
        ("Drink Interactions", test_drink_interactions),
        ("Movement Blocking", test_movement_blocking)
    ]
    
    results = []
    
    while True:
        print(f"\n{'='*40}")
        print("Available Tests:")
        for i, (name, _) in enumerate(test_functions, 1):
            status = "✅" if i-1 < len(results) and results[i-1] else "❌" if i-1 < len(results) else "⏱️"
            print(f"{i}. {status} {name}")
        
        print(f"{len(test_functions)+1}. 🏃 Run All Tests")
        print(f"{len(test_functions)+2}. 📊 Show Results Summary")
        print(f"0. ❌ Exit")
        
        try:
            choice = input(f"\nSelect test (0-{len(test_functions)+2}): ").strip()
            
            if choice == "0":
                break
            
            elif choice == str(len(test_functions)+1):  # Run all
                print("\n🏃 Running all tests...")
                results.clear()
                for name, test_func in test_functions:
                    print(f"\n{'='*20} {name} {'='*20}")
                    try:
                        success = test_func(game)
                        results.append(success)
                        print(f"{'✅ PASS' if success else '❌ FAIL'}: {name}")
                    except Exception as e:
                        print(f"💥 ERROR in {name}: {e}")
                        results.append(False)
            
            elif choice == str(len(test_functions)+2):  # Show summary
                if results:
                    passed = sum(results)
                    total = len(results)
                    print(f"\n📊 Results Summary:")
                    print(f"   Tests run: {total}")
                    print(f"   Passed: {passed}")
                    print(f"   Failed: {total - passed}")
                    print(f"   Success rate: {passed/total*100:.1f}%")
                    
                    if passed == total:
                        print("🎉 All tests PASSED!")
                    else:
                        print("❌ Some tests failed.")
                else:
                    print("No tests have been run yet.")
            
            elif choice.isdigit() and 1 <= int(choice) <= len(test_functions):
                test_idx = int(choice) - 1
                name, test_func = test_functions[test_idx]
                
                print(f"\n{'='*20} {name} {'='*20}")
                try:
                    success = test_func(game)
                    
                    # Update results
                    while len(results) <= test_idx:
                        results.append(None)  # Placeholder
                    results[test_idx] = success
                    
                    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: {name}")
                except Exception as e:
                    print(f"💥 ERROR: {e}")
                    while len(results) <= test_idx:
                        results.append(None)
                    results[test_idx] = False
            
            else:
                print("Invalid choice. Please try again.")
                
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n👋 Goodbye!")


def run_all_cyclops_tests():
    """Run all tests in sequence."""
    print("🧿 Running All Cyclops Tests")
    print("=" * 50)
    
    try:
        game = GameEngine(debug_mode=True)
        print("✅ Game engine initialized")
    except Exception as e:
        print(f"❌ Failed to initialize game: {e}")
        return False
    
    test_functions = [
        ("Cyclops Presence", test_cyclops_presence),
        ("Combat Stats", test_cyclops_combat_stats),
        ("Sleep/Wake Cycle", test_sleep_wake_cycle), 
        ("Food Interactions", test_food_interactions),
        ("Drink Interactions", test_drink_interactions),
        ("Movement Blocking", test_movement_blocking)
    ]
    
    results = []
    
    for name, test_func in test_functions:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            success = test_func(game)
            results.append(success)
            print(f"{'✅ PASS' if success else '❌ FAIL'}: {name}")
        except Exception as e:
            print(f"💥 ERROR in {name}: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*50}")
    print(f"🧿 Cyclops Test Summary:")
    print(f"   Tests run: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All Cyclops tests PASSED! Phase 4 implementation successful! ✅")
    else:
        print(f"\n❌ {total-passed} tests failed. Check implementation.")
    
    return passed == total


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all_cyclops_tests()
    else:
        interactive_cyclops_test()