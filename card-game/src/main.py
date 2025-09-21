import pygame
import sys
from gui.screen_manager import ScreenManager
from gui.menu_screen import MenuScreen
from gui.game_screen import GameScreen
from game.game import Game
from game.player import Player

def main():
    pygame.init()
    
    # Get the screen info to set fullscreen mode
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    
    # Create fullscreen display
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Card Game")
    
    # Create game instance
    game = Game()
    
    # Create screens
    menu_screen = MenuScreen(screen)
    game_screen = GameScreen(screen, game)
    
    # Create and set up screen manager
    manager = ScreenManager()
    manager.add_screen("menu", menu_screen)
    manager.add_screen("game", game_screen)
    manager.set_screen("menu")
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            # Handle events with current screen
            if manager.current_screen:
                action = None
                
                # Check for menu actions
                if manager.current_screen == menu_screen and event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_screen.start_button.collidepoint(pygame.mouse.get_pos()):
                        # Set up the game with human player vs computer
                        game.deck = game.create_deck()
                        game.start_game()  # This will set up players and deal cards
                        manager.set_screen("game")
                    elif menu_screen.quit_button.collidepoint(pygame.mouse.get_pos()):
                        running = False
                        break
                
                # Let the current screen handle other events
                manager.current_screen.handle_events(event)
                
                # Check if game has ended and needs to return to menu
                if manager.current_screen == game_screen and not game.is_running:
                    # Reset and go back to menu
                    manager.set_screen("menu")
        
        # Update game state
        manager.update()
        
        # Draw current screen
        screen.fill((0, 0, 0))  # Clear screen
        manager.draw(screen)
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()