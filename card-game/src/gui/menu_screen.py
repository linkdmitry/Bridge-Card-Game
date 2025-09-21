import pygame
from pygame import font, display, draw, Rect

class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        # Get screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Scale font size based on screen height
        font_size = min(int(self.screen_height * 0.12), 80)
        self.font = font.Font(None, font_size)
        self.title = self.font.render("Card Game", True, (255, 255, 255))
        
        # Calculate button dimensions based on screen size
        button_width = min(self.screen_width * 0.6, 600)
        button_height = min(self.screen_height * 0.15, 100)
        button_x = (self.screen_width - button_width) / 2
        
        # Position buttons with proper spacing
        self.start_button = Rect(button_x, self.screen_height * 0.4, button_width, button_height)
        self.quit_button = Rect(button_x, self.screen_height * 0.6, button_width, button_height)
        self.action = None

    def draw(self, surface):
        """Draw the menu screen"""
        surface.fill((0, 0, 0))
        
        # Draw title centered at the top
        title_rect = self.title.get_rect(center=(self.screen_width / 2, self.screen_height * 0.15))
        surface.blit(self.title, title_rect)
        
        # Draw start button (green)
        draw.rect(surface, (0, 255, 0), self.start_button)
        self.draw_text("Start Game", self.start_button, surface)
        
        # Draw quit button (red)
        draw.rect(surface, (255, 0, 0), self.quit_button)
        self.draw_text("Quit", self.quit_button, surface)
        
        # Add fullscreen toggle hint
        small_font = pygame.font.Font(None, 24)
        hint_text = small_font.render("Press ESC or F11 to toggle fullscreen mode", True, (255, 255, 0))
        hint_rect = hint_text.get_rect(center=(self.screen_width / 2, self.screen_height * 0.9))
        surface.blit(hint_text, hint_rect)

    def draw_text(self, text, rect, surface):
        """Draw text centered in a rectangle"""
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

    def handle_events(self, event):
        """Handle menu events and return actions"""
        if event.type == pygame.KEYDOWN:
            # Handle keys for toggling fullscreen mode
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F11:
                # Toggle fullscreen mode
                pygame.display.toggle_fullscreen()
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(pygame.mouse.get_pos()):
                return "start_game"
            if self.quit_button.collidepoint(pygame.mouse.get_pos()):
                return "quit"
        return None
    
    def update(self):
        """Update menu state (no updates needed for now)"""
        pass
    
    def on_enter(self):
        """Called when this screen becomes active"""
        # Update dimensions in case resolution changed
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
    
    def display(self):
        self.draw(self.screen)
        display.flip()