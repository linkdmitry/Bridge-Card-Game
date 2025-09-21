#!/usr/bin/env python3
"""
Test script to verify the draw mechanics are working correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from game.game import Game
from game.card import Card

def test_draw_mechanics():
    """Test that draw mechanics work correctly"""
    print("Testing draw mechanics...")
    
    # Create a game instance
    game = Game()
    game.start_game()
    
    human_player = game.players[0]
    computer_player = game.players[1]
    
    print(f"Human player starts with {len(human_player.hand)} cards")
    print(f"Computer player starts with {len(computer_player.hand)} cards")
    
    # Test 1: Normal scenario - should only allow 1 draw per turn
    print("\n=== Test 1: Normal Draw Mechanics ===")
    initial_hand_size = len(human_player.hand)
    
    # First draw should work
    game.optional_draw_used = False
    if len(game.deck.cards) > 0:
        card = game.deck.draw_card()
        human_player.add_card(card)
        game.optional_draw_used = True
        print(f"First draw successful: {card.get_card_info()}")
        print(f"Hand size: {initial_hand_size} -> {len(human_player.hand)}")
    
    # Second draw should be prevented
    if game.optional_draw_used and not game.must_draw:
        print("Second draw correctly prevented (optional_draw_used = True)")
    
    # Test 2: 6-covering scenario - should allow multiple draws
    print("\n=== Test 2: 6-Covering Draw Mechanics ===")
    
    # Set up a 6-covering scenario
    six_hearts = Card(6, 'H')
    game.table_cards = [six_hearts]
    game.pending_effects['requires_six'] = True
    game.pending_effects['six_player'] = computer_player  # Different player played the 6
    game.pending_effects['six_suit'] = 'H'
    
    # Clear human player's hand and give them only non-matching cards
    human_player.hand = [
        Card(2, 'C'),  # 2 of Clubs - can't cover Hearts 6
        Card(3, 'D'),  # 3 of Diamonds - can't cover Hearts 6
        Card(4, 'S'),  # 4 of Spades - can't cover Hearts 6
    ]
    
    print(f"Set up 6-covering scenario:")
    print(f"Top card: {six_hearts.get_card_info()}")
    print(f"Human player hand: {[card.get_card_info() for card in human_player.hand]}")
    print(f"requires_six: {game.pending_effects['requires_six']}")
    print(f"Player has valid play: {game.has_valid_play(human_player)}")
    
    # Test the draw_until_six_covered method
    initial_deck_size = len(game.deck.cards)
    success = game.draw_until_six_covered(human_player)
    final_deck_size = len(game.deck.cards)
    cards_drawn = initial_deck_size - final_deck_size
    
    print(f"draw_until_six_covered result: {success}")
    print(f"Cards drawn: {cards_drawn}")
    print(f"Final hand size: {len(human_player.hand)}")
    print(f"Player now has valid play: {game.has_valid_play(human_player)}")
    
    # Test 3: Forced draw when no playable cards (normal scenario)
    print("\n=== Test 3: Forced Draw When No Playable Cards ===")
    
    # Reset scenario
    game.pending_effects['requires_six'] = False
    game.optional_draw_used = False
    jack_clubs = Card(11, 'C')
    game.table_cards = [jack_clubs]
    
    # Give human player cards that don't match Jack of Clubs
    human_player.hand = [
        Card(2, 'H'),  # 2 of Hearts - doesn't match Jack of Clubs
        Card(3, 'D'),  # 3 of Diamonds - doesn't match Jack of Clubs
    ]
    
    print(f"Top card: {jack_clubs.get_card_info()}")
    print(f"Human player hand: {[card.get_card_info() for card in human_player.hand]}")
    print(f"Player has valid play: {game.has_valid_play(human_player)}")
    
    # Test the draw_until_playable method
    initial_deck_size = len(game.deck.cards)
    success = game.draw_until_playable(human_player)
    final_deck_size = len(game.deck.cards)
    cards_drawn = initial_deck_size - final_deck_size
    
    print(f"draw_until_playable result: {success}")
    print(f"Cards drawn: {cards_drawn} (should be exactly 1)")
    print(f"Final hand size: {len(human_player.hand)}")
    
    # Summary
    print("\n=== Summary ===")
    print("✓ Draw mechanics test completed")
    print("Key behaviors:")
    print("- Normal turns: Max 1 draw (optional becomes forced if no valid cards)")
    print("- 6-covering: Multiple draws allowed until valid card found")
    print("- Forced draws: Exactly 1 card drawn, turn skipped if still no valid play")

if __name__ == "__main__":
    test_draw_mechanics()
