#!/usr/bin/env python3
"""
Test script to verify suit enforcement after Jack cards
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from game.game import Game
from game.card import Card

def test_suit_enforcement():
    """Test that suit enforcement works correctly after playing a Jack"""
    print("Testing suit enforcement after Jack cards...")
    
    # Create a game instance
    game = Game()
    game.start_game()
    
    # Create test cards
    jack_hearts = Card(11, 'H')  # Jack of Hearts
    five_hearts = Card(5, 'H')   # 5 of Hearts (should be valid after Jack chooses Hearts)
    five_clubs = Card(5, 'C')    # 5 of Clubs (should be invalid after Jack chooses Hearts)
    jack_spades = Card(11, 'S')  # Jack of Spades (should always be valid)
    
    # Place the Jack on the table and set suit enforcement
    game.table_cards = [jack_hearts]
    game.pending_effects['suit_enforced'] = True
    game.pending_effects['chosen_suit'] = 'H'  # Hearts chosen
    
    print(f"Table top card: {jack_hearts.get_card_info()}")
    print(f"Enforced suit: Hearts")
    print(f"Suit enforcement active: {game.pending_effects['suit_enforced']}")
    
    # Test 1: Hearts card should be valid
    can_play_hearts = game.can_play_card(five_hearts)
    print(f"Can play {five_hearts.get_card_info()}: {can_play_hearts} (Expected: True)")
    
    # Test 2: Clubs card should be invalid
    can_play_clubs = game.can_play_card(five_clubs)
    print(f"Can play {five_clubs.get_card_info()}: {can_play_clubs} (Expected: False)")
    
    # Test 3: Jack should always be valid
    can_play_jack = game.can_play_card(jack_spades)
    print(f"Can play {jack_spades.get_card_info()}: {can_play_jack} (Expected: True)")
      # Test 4: Check that enforcement is reset after playing a matching card
    game.apply_card_effects(five_hearts, game.players[0])
    # Simulate actually playing the card by adding it to the table
    game.table_cards.append(five_hearts)
    print(f"After playing Hearts card, suit enforcement active: {game.pending_effects['suit_enforced']} (Expected: False)")
    
    # Test 5: After enforcement is reset, Clubs card should be valid (matches rank with 5 of Hearts)
    can_play_clubs_after = game.can_play_card(five_clubs)
    print(f"Can play {five_clubs.get_card_info()} after enforcement reset: {can_play_clubs_after} (Expected: True)")
    
    # Summary
    tests_passed = 0
    total_tests = 5
    
    if can_play_hearts:
        tests_passed += 1
        print("✓ Test 1 PASSED: Hearts card valid when Hearts enforced")
    else:
        print("✗ Test 1 FAILED: Hearts card should be valid when Hearts enforced")
    
    if not can_play_clubs:
        tests_passed += 1
        print("✓ Test 2 PASSED: Clubs card invalid when Hearts enforced")
    else:
        print("✗ Test 2 FAILED: Clubs card should be invalid when Hearts enforced")
    
    if can_play_jack:
        tests_passed += 1
        print("✓ Test 3 PASSED: Jack is always valid")
    else:
        print("✗ Test 3 FAILED: Jack should always be valid")
    
    if not game.pending_effects['suit_enforced']:
        tests_passed += 1
        print("✓ Test 4 PASSED: Enforcement reset after playing matching card")
    else:
        print("✗ Test 4 FAILED: Enforcement should be reset after playing matching card")
    
    if can_play_clubs_after:
        tests_passed += 1
        print("✓ Test 5 PASSED: Clubs card valid after enforcement reset")
    else:
        print("✗ Test 5 FAILED: Clubs card should be valid after enforcement reset")
    
    print(f"\nTest Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests PASSED! Suit enforcement is working correctly.")
        return True
    else:
        print("❌ Some tests FAILED. Suit enforcement needs fixing.")
        return False

if __name__ == "__main__":
    test_suit_enforcement()
