import pygame

class Button:
    def __init__(self, text, position, action=None):
        self.position = position
        self.text = text
        self.width = 200
        self.height = 50
        self.rect = pygame.Rect(position[0], position[1], self.width, self.height)
        self.color = (100, 100, 200)
        self.hover_color = (150, 150, 250)
        self.font = pygame.font.Font(None, 36)
        self.action = action

    def draw(self, screen):
        current_color = self.color
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            current_color = self.hover_color
        pygame.draw.rect(screen, current_color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]
        
    def click(self):
        if self.action:
            self.action()