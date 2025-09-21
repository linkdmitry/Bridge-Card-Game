#!/usr/bin/env python3
"""
Quick test script to verify player effect indicators are working
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from game.game import Game
from game.card import Card

def test_effect_indicators():
    """Test that effect indicators are properly set when card effects are applied"""
    
    game = Game()
    
    # Mock callback to track effect notifications
    effect_notifications = []
    
    def mock_callback(player_index, effect_type):
        effect_notifications.append((player_index, effect_type))
        print(f"Effect notification: Player {player_index} -> {effect_type}")
    
    # Set up the callback
    game.set_player_effect_callback(mock_callback)
    
    # Start a game
    game.start_game()
    
    # Simulate playing an 8 (causes next player to draw 2 and skip turn)
    print("Testing 8 card effect...")
    human_player = game.players[0]
    computer_player = game.players[1]
    
    # Add an 8 to human player's hand
    eight_card = Card(8, "Hearts")
    human_player.hand.append(eight_card)
    
    # Set up table for valid play
    game.table_cards = [Card(7, "Hearts")]
    
    # Play the 8
    if game.play_card(human_player, len(human_player.hand) - 1):
        print("✓ 8 card played successfully")
        
        # Switch turns (this should trigger the draw effect)
        game.next_turn()
        
        # Check if effect notification was triggered
        if effect_notifications:
            print(f"✓ Effect notification triggered: {effect_notifications[-1]}")
        else:
            print("✗ No effect notification triggered")
    
    print(f"Total notifications: {len(effect_notifications)}")
    for notification in effect_notifications:
        print(f"  - {notification}")

if __name__ == "__main__":
    test_effect_indicators()
