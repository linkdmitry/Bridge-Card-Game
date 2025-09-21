import pygame
import os
import sys

def create_card_back():
    # Initialize pygame
    pygame.init()
    
    # Set up paths
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(src_dir, "images")
    
    # Use ace of spades as a template
    template_path = os.path.join(images_dir, "ace_of_spades2.png")
    output_path = os.path.join(images_dir, "card_back.png")
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found: {template_path}")
        return False
        
    try:
        # Load the template
        card_img = pygame.image.load(template_path)
        
        # Get the dimensions
        width, height = card_img.get_size()
        
        # Create a new surface for the card back
        card_back = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Fill with a dark blue color
        card_back.fill((20, 30, 120))
        
        # Add a pattern
        for i in range(0, width, 10):
            pygame.draw.line(card_back, (30, 50, 150), (i, 0), (i, height), 3)
        
        for j in range(0, height, 10):
            pygame.draw.line(card_back, (30, 50, 150), (0, j), (width, j), 1)
            
        # Add a border
        pygame.draw.rect(card_back, (200, 200, 255), (0, 0, width, height), 4)
        
        # Add a decorative design in the center
        center_x, center_y = width // 2, height // 2
        pygame.draw.circle(card_back, (200, 200, 255), (center_x, center_y), width // 4, 3)
        pygame.draw.circle(card_back, (200, 200, 255), (center_x, center_y), width // 6, 2)
        
        # Save the card back
        pygame.image.save(card_back, output_path)
        print(f"Card back created successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error creating card back: {e}")
        return False

if __name__ == "__main__":
    create_card_back()
