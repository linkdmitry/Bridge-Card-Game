import pygame
import os

class CardRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.card_images = {}
        self.card_back = None
        self.load_images()
        
    def load_images(self):
        """Load card images from images folder or create default card visuals"""
        # Get the absolute path to the images folder
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(current_dir, 'images')
        print(f"Looking for card images in: {image_path}")
        
        if os.path.exists(image_path):
            try:
                # Load all card images
                suits = ['clubs', 'diamonds', 'hearts', 'spades']
                ranks = {
                    1: 'ace',
                    2: '2',
                    3: '3',
                    4: '4',
                    5: '5',
                    6: '6',
                    7: '7',
                    8: '8',
                    9: '9',
                    10: '10',
                    11: 'jack',
                    12: 'queen',
                    13: 'king'
                }
                
                # Card dimensions (may need to scale images)
                card_width, card_height = 80, 120
                
                # Load each card image
                for suit in suits:
                    for rank_num, rank_name in ranks.items():
                        # Convert suit to proper case for our game logic
                        suit_proper = suit.capitalize()
                        # For face cards, use the first version (without '2' suffix)
                        filename = f"{rank_name}_of_{suit}.png"
                        file_path = os.path.join(image_path, filename)
                        
                        if os.path.exists(file_path):
                            # Load and scale the image
                            card_img = pygame.image.load(file_path)
                            card_img = pygame.transform.scale(card_img, (card_width, card_height))
                            self.card_images[(rank_num, suit_proper)] = card_img
                
                # Load the card back image
                back_file_path = os.path.join(image_path, "card_back.png")
                
                # If the card_back.png doesn't exist, check for alternative card back options
                if not os.path.exists(back_file_path):
                    back_file_path = os.path.join(image_path, "red_joker.png")
                
                # If no specific card back is found, create one dynamically
                if os.path.exists(back_file_path):
                    # Load the card back image
                    self.card_back = pygame.image.load(back_file_path)
                    
                    # Scale to our card dimensions
                    self.card_back = pygame.transform.scale(self.card_back, (card_width, card_height))
                    print(f"Loaded card back from: {back_file_path}")
                
                # If all cards were successfully loaded, return
                if len(self.card_images) == 52 and self.card_back is not None:
                    print("Successfully loaded all card images")
                    return
                    
                print(f"Loaded {len(self.card_images)} card images")
                    
            except Exception as e:
                print(f"Error loading card images: {e}")
        
        # If no card images found or failed to load, create simple colored rectangles
        print("Using default card visuals")
        self.create_default_card_images()
            
    def create_default_card_images(self):
        """Create simple colored rectangles for cards if no images are available"""
        suits = {'Hearts': (255, 0, 0), 'Diamonds': (255, 0, 0), 
                'Clubs': (0, 0, 0), 'Spades': (0, 0, 0)}
        
        for suit, color in suits.items():
            for rank in range(1, 14):
                card_surface = pygame.Surface((80, 120))
                card_surface.fill((255, 255, 255))  # White background
                pygame.draw.rect(card_surface, (200, 200, 200), (2, 2, 76, 116), 2)  # Border
                
                # Draw rank and suit
                font = pygame.font.Font(None, 36)
                rank_text = self.get_rank_text(rank)
                text = font.render(rank_text, True, color)
                card_surface.blit(text, (10, 10))
                
                # Draw suit symbol
                suit_text = self.get_suit_symbol(suit)
                text = font.render(suit_text, True, color)
                card_surface.blit(text, (40, 60))
                
                self.card_images[(rank, suit)] = card_surface
        
        # Create card back
        self.card_back = pygame.Surface((80, 120))
        self.card_back.fill((30, 30, 150))  # Blue background
        pygame.draw.rect(self.card_back, (200, 200, 200), (2, 2, 76, 116), 2)  # Border
        
        # Add some pattern to the back
        for i in range(0, 70, 10):
            pygame.draw.rect(self.card_back, (20, 20, 120), (10 + i, 10, 5, 100))  # Vertical stripes
    
    def get_rank_text(self, rank):
        if rank == 1:
            return "A"
        elif rank == 11:
            return "J"
        elif rank == 12:
            return "Q"
        elif rank == 13:
            return "K"
        else:
            return str(rank)
            
    def get_suit_symbol(self, suit):
        if suit == "Hearts":
            return "♥"
        elif suit == "Diamonds":
            return "♦"
        elif suit == "Clubs":
            return "♣"
        else:  # Spades
            return "♠"
        
    def render_card(self, card, position):
        """Render a single card at the specified position."""
        key = (card.rank, card.suit)
        if key in self.card_images:
            self.screen.blit(self.card_images[key], position)
        else:
            # Create a default card visual if image not found
            pygame.draw.rect(self.screen, (255, 255, 255), (position[0], position[1], 80, 120))
            font = pygame.font.Font(None, 24)
            text = font.render(card.get_card_info(), True, (0, 0, 0))
            self.screen.blit(text, (position[0] + 5, position[1] + 50))
            print(f"Missing card image for {card.get_card_info()}")

    def render_card_back(self, position):
        """Render the back of a card at the specified position."""
        if self.card_back:
            self.screen.blit(self.card_back, position)
        else:
            # Fallback if card back isn't available
            pygame.draw.rect(self.screen, (30, 30, 150), (position[0], position[1], 80, 120))
            pygame.draw.rect(self.screen, (200, 200, 200), (position[0]+2, position[1]+2, 76, 116), 2)
            print("Missing card back image")
            
    def render_hand(self, player, position=(50, 400)):
        """Render the player's hand of cards."""
        for i, card in enumerate(player.hand):
            self.render_card(card, (position[0] + i * 90, position[1]))