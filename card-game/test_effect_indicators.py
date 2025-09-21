#!/usr/bin/env python3
"""
Test script to verify that player effect indicators work correctly
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from game.game import Game
from game.card import Card
from gui.game_screen import GameScreen
import pygame

def test_effect_indicators():
    """Test that effect indicators are displayed when players are affected by card effects"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Create game and game screen
    game = Game()
    game.start_game()
    game_screen = GameScreen(screen, game)
    
    print("Testing effect indicator system...")
    
    # Test 1: Skip turn effect
    print("\n1. Testing skip turn effect...")
    game_screen.on_player_effect_notification(1, "skip_turn", 3000)  # Computer affected
    assert game_screen.player_effect_indicators[1] == "skip_turn"
    print("✓ Skip turn indicator set for computer")
    
    # Test 2: Draw cards effect
    print("\n2. Testing draw cards effect...")
    game_screen.on_player_effect_notification(0, "draw_2", 3000)  # Human affected
    assert game_screen.player_effect_indicators[0] == "draw_2"
    print("✓ Draw cards indicator set for human player")
    
    # Test 3: Clear effect indicators
    print("\n3. Testing clear effect indicators...")
    game_screen.on_player_effect_notification(1, None, 0)  # Clear computer
    assert game_screen.player_effect_indicators[1] is None
    print("✓ Computer effect indicator cleared")
    
    game_screen.on_player_effect_notification(0, None, 0)  # Clear human
    assert game_screen.player_effect_indicators[0] is None
    print("✓ Human effect indicator cleared")
    
    print("\n✅ All effect indicator tests passed!")
    
    pygame.quit()

if __name__ == "__main__":
    test_effect_indicators()
