#!/usr/bin/env python3
"""
Test script to verify the 6-covering rule is working correctly after the fix
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from game.game import Game
from game.card import Card

def test_six_covering_rule():
    """Test that the 6-covering rule works correctly"""
    print("Testing 6-covering rule...")
    
    game = Game()
    game.start_game()
    
    human_player = game.players[0]  # Player 0
    computer_player = game.players[1]  # Player 1
    
    # Test 1: Player who played 6 can cover it with another 6
    print("\n=== Test 1: Same player can cover 6 with another 6 ===")
    six_hearts = Card(6, 'H')
    six_clubs = Card(6, 'C')
    
    game.table_cards = [six_hearts]
    game.pending_effects['requires_six'] = True
    game.pending_effects['six_player'] = human_player
    game.pending_effects['six_suit'] = 'H'
    game.current_player_index = 0  # Human player's turn
    
    can_play_six = game.can_play_card(six_clubs)
    print(f"Human can play {six_clubs.get_card_info()} on their own {six_hearts.get_card_info()}: {can_play_six} (Expected: True)")
    
    # Test 2: Player who played 6 can cover it with same suit
    print("\n=== Test 2: Same player can cover 6 with same suit ===")
    five_hearts = Card(5, 'H')
    
    can_play_same_suit = game.can_play_card(five_hearts)
    print(f"Human can play {five_hearts.get_card_info()} on their own {six_hearts.get_card_info()}: {can_play_same_suit} (Expected: True)")
    
    # Test 3: Player who played 6 can cover it with Jack
    print("\n=== Test 3: Same player can cover 6 with Jack ===")
    jack_spades = Card(11, 'S')
    
    can_play_jack = game.can_play_card(jack_spades)
    print(f"Human can play {jack_spades.get_card_info()} on their own {six_hearts.get_card_info()}: {can_play_jack} (Expected: True)")
    
    # Test 4: Different player CANNOT interfere with opponent's 6 - even with Jack
    print("\n=== Test 4: Different player cannot interfere with opponent's 6 ===")
    game.current_player_index = 1  # Switch to computer player's turn
    
    can_computer_play_jack = game.can_play_card(jack_spades)
    print(f"Computer can play {jack_spades.get_card_info()} on human's {six_hearts.get_card_info()}: {can_computer_play_jack} (Expected: False)")
    
    # Test 5: Different player CANNOT interfere with any card
    print("\n=== Test 5: Different player cannot interfere with any card ===")
    seven_hearts = Card(7, 'H')  # Same suit as the 6
    
    can_computer_play_same_suit = game.can_play_card(seven_hearts)
    print(f"Computer can play {seven_hearts.get_card_info()} on human's {six_hearts.get_card_info()}: {can_computer_play_same_suit} (Expected: False)")
    
    # Test 6: When computer plays a 6, human cannot interfere
    print("\n=== Test 6: Human cannot interfere with computer's 6 ===")
    six_diamonds = Card(6, 'D')
    game.table_cards = [six_diamonds]
    game.pending_effects['six_player'] = computer_player
    game.pending_effects['six_suit'] = 'D'
    game.current_player_index = 0  # Human player's turn
    
    jack_hearts = Card(11, 'H')
    can_human_play_jack = game.can_play_card(jack_hearts)
    print(f"Human can play {jack_hearts.get_card_info()} on computer's {six_diamonds.get_card_info()}: {can_human_play_jack} (Expected: False)")
    
    # Summary
    tests_passed = 0
    total_tests = 6
    
    if can_play_six:
        tests_passed += 1
        print("✓ Test 1 PASSED: Same player can cover 6 with another 6")
    else:
        print("✗ Test 1 FAILED: Same player should be able to cover 6 with another 6")
    
    if can_play_same_suit:
        tests_passed += 1
        print("✓ Test 2 PASSED: Same player can cover 6 with same suit")
    else:
        print("✗ Test 2 FAILED: Same player should be able to cover 6 with same suit")
    
    if can_play_jack:
        tests_passed += 1
        print("✓ Test 3 PASSED: Same player can cover 6 with Jack")
    else:
        print("✗ Test 3 FAILED: Same player should be able to cover 6 with Jack")
    
    if not can_computer_play_jack:
        tests_passed += 1
        print("✓ Test 4 PASSED: Different player cannot interfere with opponent's 6 (even with Jack)")
    else:
        print("✗ Test 4 FAILED: Different player should not be able to interfere with opponent's 6")
    
    if not can_computer_play_same_suit:
        tests_passed += 1
        print("✓ Test 5 PASSED: Different player cannot interfere with any card")
    else:
        print("✗ Test 5 FAILED: Different player should not be able to interfere with any card")
    
    if not can_human_play_jack:
        tests_passed += 1
        print("✓ Test 6 PASSED: Human cannot interfere with computer's 6")
    else:
        print("✗ Test 6 FAILED: Human should not be able to interfere with computer's 6")
    
    print(f"\nTest Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests PASSED! 6-covering rule is working correctly.")
        return True
    else:
        print("❌ Some tests FAILED. 6-covering rule needs fixing.")
        return False

if __name__ == "__main__":
    test_six_covering_rule()
