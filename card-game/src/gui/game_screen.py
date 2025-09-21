import pygame
import math  # Added for math.sin()
from game.game import Game
from gui.button import Button
from gui.card_renderer import CardRenderer
from utils.helpers import get_messages, clear_messages

class GameScreen:
    def __init__(self, screen, game: Game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 28)
        self.card_renderer = CardRenderer(screen)
        self.error_message = None      # Message to display when an invalid move is made
        self.error_time = 0            # Time when error message was displayed
        
        # Cards staged for playing during the turn
        self.staged_cards = []         # Indices of cards staged to be played
        self.staged_cards_valid = True # Whether the staged cards are valid to play
        
        # Suit selection variables
        self.waiting_for_suit_choice = False
        self.jack_indices = []  # Store indices of Jack cards being played
        self.suit_buttons = []
        
        # Computer suit selection indicator
        self.computer_choosing_suit = False
        self.computer_choice_start_time = 0
        self.computer_choice_duration = 2000  # Show indicator for 2 seconds
        
        # Player effect indicators - track which players are affected by card effects
        self.player_effect_indicators = {
            0: None,  # Human player (index 0)
            1: None   # Computer player (index 1)
        }
        
        # Get screen dimensions for positioning
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Define warm color palette
        self.colors = {
            'bg_panel': (85, 60, 40),           # Warm brown background
            'panel_border': (180, 130, 90),     # Light brown border
            'text_primary': (255, 235, 200),    # Warm white
            'text_secondary': (245, 200, 140),  # Warm beige
            'text_highlight': (255, 180, 80),   # Warm orange
            'text_warning': (255, 120, 80),     # Warm red-orange
            'text_success': (200, 255, 120),    # Warm green
            'text_error': (255, 100, 100),      # Warm red
            'card_select_primary': (255, 200, 0),   # Golden yellow
            'card_select_secondary': (255, 150, 50), # Orange
            'card_playable': (100, 200, 80),    # Warm green
            'table_color': (60, 120, 60),       # Warm forest green
            'button_highlight': (220, 160, 100), # Warm tan
            'message_log_bg': (70, 50, 35),     # Darker brown for message log
            'message_text': (245, 220, 180)     # Light tan for message text
        }
        
        # Define panel dimensions
        # Right side: Info panel 
        self.info_panel_width = min(350, self.screen_width * 0.3)
        self.info_panel_x = self.screen_width - self.info_panel_width
        
        # Left side: Message log panel
        self.message_panel_width = min(300, self.screen_width * 0.25)
        self.message_panel_x = 0
        
        # Center: Game area
        self.game_area_x = self.message_panel_width + 10
        self.game_area_width = self.info_panel_x - self.game_area_x - 10
        
        # Position buttons in the bottom-left corner, stacked vertically
        button_x_offset = 20  # Left margin from screen edge
        button_y_offset = self.screen_height - 200  # Start from bottom, with room for 4 buttons
        button_spacing = 45  # Vertical space between buttons
        
        self.buttons = [
            Button("Draw Card", (button_x_offset, button_y_offset), self.draw_card),
            Button("Finish Turn", (button_x_offset, button_y_offset + button_spacing), self.finish_turn),
            Button("Clear Staged", (button_x_offset, button_y_offset + button_spacing * 2), self.clear_staged_cards),
            Button("End Game", (button_x_offset, button_y_offset + button_spacing * 3), self.quit_game)
        ]
        
        # Position next round button at center of game area
        self.new_round_button = Button("Next Round", (self.game_area_x + self.game_area_width // 2, self.screen_height * 0.7), self.start_new_round)
        self.show_new_round_button = False  # Only show this button between rounds
        
        # Set up callback for player effect notifications
        self.game.set_player_effect_callback(self.on_player_effect_notification)

    def clear_staged_cards(self):
        """Clear any cards that were staged but not played"""
        if self.staged_cards:
            self.staged_cards = []
            self.set_message("Cleared all staged cards")
            
    def stage_card(self, card_index):
        """Stage a card for playing later"""
        # Get the player's hand
        human_player = self.game.players[0]
        card = human_player.hand[card_index]

        # Check if the card can be played
        if not self.game.can_play_card(card):
            # Access the top card from table_cards instead of using a non-existent top_card attribute
            top_card = self.game.table_cards[-1] if self.game.table_cards else None
            if top_card:
                self.set_message(f"Cannot play {card.get_card_info()} on {top_card.get_card_info()}")
            else:
                self.set_message(f"Cannot play {card.get_card_info()} - no cards on table")
            return False

        # If this is the first card staged, just add it
        if not self.staged_cards:
            self.staged_cards.append(card_index)
            self.set_message(f"Staged {card.get_card_info()}")
            return True
        
        # If we already have cards staged, check that the new card has the same rank
        first_staged_card = human_player.hand[self.staged_cards[0]]
        if card.rank != first_staged_card.rank:
            self.set_message(f"Can only stage cards of the same rank. Current staged rank: {first_staged_card.rank}")
            return False
        
        # Add the card to staged cards
        self.staged_cards.append(card_index)
        self.set_message(f"Staged {card.get_card_info()}")
        return True
            
    def finish_turn(self):
        """Play all staged cards and end the turn"""
        if not self.staged_cards:
            self.set_message("No cards staged to play")
            return
        
        # Get the player's hand
        human_player = self.game.players[0]
        
        # Save the cards for messaging
        cards_to_play = [human_player.hand[i] for i in self.staged_cards]
        card_info = ", ".join([card.get_card_info() for card in cards_to_play])
        
        # Check if we're trying to play Jack cards - if so, handle suit selection
        if cards_to_play and cards_to_play[0].rank == 11:
            # Jack cards require suit selection
            if not self.waiting_for_suit_choice:
                self.jack_indices = self.staged_cards.copy()
                self.waiting_for_suit_choice = True
                self.create_suit_selection_buttons()  # Create the suit selection interface
                self.set_message("Select a suit for the Jack")
                return
        
        # Play all the cards at once using play_cards
        chosen_suit = self.pending_suit_choice if hasattr(self, 'pending_suit_choice') else None
        if not self.game.play_cards(human_player, self.staged_cards, chosen_suit):
            self.set_message(f"Failed to play {card_info}")
            self.staged_cards = []
            if self.waiting_for_suit_choice:
                self.waiting_for_suit_choice = False
            return
        
        # All cards were played successfully
        self.set_message(f"Played {card_info}")
        self.staged_cards = []
        
        # Clear suit selection mode if active
        if self.waiting_for_suit_choice:
            self.waiting_for_suit_choice = False
            if hasattr(self, 'pending_suit_choice'):
                delattr(self, 'pending_suit_choice')
        
        # End the player's turn
        self.game.end_player_turn()
        
        # Check for win condition
        if len(human_player.hand) == 0:
            self.set_message("You win!")
            self.show_new_round_button = True
        else:
            # Let the AI take its turn
            self.process_ai_turns()

    def play_card(self, card_index=None):
        """Play a card directly or handle old API call"""
        # If this is called with no parameters (old button click), ignore
        if card_index is None:
            return
            
        # Otherwise stage the card
        self.stage_card(card_index)
        
    def set_message(self, message, is_error=False):
        """Set error message and log it to the message system"""
        self.error_message = message
        self.error_time = pygame.time.get_ticks()
        
        # Log the message using the helper function
        from utils.helpers import display_message
        display_message(message)

    def draw(self, surface):
        """Draw the game screen"""
        if not self.game.is_running and not self.game.round_end_message:
            return False  # Nothing to draw
            
        # Draw the table setup first
        self.draw_table_setup(surface)
        
        # Draw the message log window (left side)
        self.draw_message_log(surface)
        
        # Draw the information panel (right side)
        self.draw_info_panel(surface)
        
        # Draw the suit selection interface if needed
        self.draw_suit_selection(surface)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
        
        # Draw the new round button between rounds if it should be shown
        if self.show_new_round_button:
            self.new_round_button.draw(surface)
        
        # Show game over overlay if needed
        if not self.game.is_running or self.game.round_end_message:
            self.show_game_over(surface)
            
        # Draw computer suit choice visual indicator if active
        if self.game.pending_effects.get('computer_choosing_suit', False):
            self.draw_computer_choosing_suit(surface)
            current_time = pygame.time.get_ticks()
            if current_time - self.computer_choice_start_time >= self.computer_choice_duration:
                self.game.pending_effects['computer_choosing_suit'] = False
                
        # Always update the screen
        return True

    def draw_table_setup(self, surface):
        """Draw the table with players sitting across from each other"""
        # Get current screen dimensions for game area (excluding info panel)
        screen_width = self.game_area_width
        screen_height = self.screen_height
        center_x = screen_width // 2
        
        # First draw the computer's cards (at the top, facing down)
        computer_player = self.game.players[1]
        text = self.font.render("Computer", True, self.colors['text_primary'])
        text_rect = text.get_rect(center=(center_x, screen_height * 0.08))
        surface.blit(text, text_rect)
        
        # Draw effect indicator for computer if affected by card effects
        if self.player_effect_indicators[1]:
            effect = self.player_effect_indicators[1]
            if effect == "skip_turn":
                indicator_text = "⚠ SKIP TURN"
                color = self.colors['text_error']
            elif effect.startswith("draw_"):
                draw_count = effect.split("_")[1]
                indicator_text = f"⚠ DRAW {draw_count}"
                color = self.colors['text_warning']
            else:
                indicator_text = "⚠ CARD EFFECTS"
                color = self.colors['text_error']
                
            indicator_surface = self.small_font.render(indicator_text, True, color)
            indicator_rect = indicator_surface.get_rect()
            indicator_rect.centerx = center_x
            indicator_rect.top = text_rect.bottom + 5
            
            # Draw background for indicator
            padding = 5
            bg_rect = pygame.Rect(indicator_rect.x - padding, indicator_rect.y - padding, 
                                indicator_rect.width + padding*2, indicator_rect.height + padding*2)
            bg_color = (80, 40, 20) if effect.startswith("draw_") else (120, 20, 20)
            pygame.draw.rect(surface, bg_color, bg_rect)
            pygame.draw.rect(surface, color, bg_rect, 2)
            
            surface.blit(indicator_surface, indicator_rect)
        
        # Draw computer's hand face down
        computer_card_start_x = center_x - (len(computer_player.hand) * 45)  # Center cards
        for j in range(len(computer_player.hand)):
            self.card_renderer.render_card_back((computer_card_start_x + j * 90, screen_height * 0.15))
        
        # Draw the center table where cards are played
        # Draw a slightly lighter circle in the middle of the table
        center_y = screen_height // 2
        ellipse_width = min(screen_width, screen_height) * 0.4
        ellipse_height = min(screen_width, screen_height) * 0.3
        pygame.draw.ellipse(surface, self.colors['table_color'], 
                          (center_x - ellipse_width/2, center_y - ellipse_height/2, 
                           ellipse_width, ellipse_height))
        
        # Draw the deck - highlight if player must draw
        deck_pos = (center_x - ellipse_width/3, center_y)
        if self.game.deck.cards:
            # Highlight the deck if player must draw
            if self.game.must_draw:
                # Draw a pulsing highlight around the deck
                highlight_color = self.colors['text_warning']
                pygame.draw.rect(surface, highlight_color, 
                              (deck_pos[0] - 5, deck_pos[1] - 5, 90, 130), 3)
                
                # Add a message above the deck
                draw_msg = self.small_font.render("Draw Cards!", True, self.colors['text_warning'])
                surface.blit(draw_msg, (deck_pos[0] - 10, deck_pos[1] - 25))
                
            self.card_renderer.render_card_back(deck_pos)
            deck_count = self.font.render(f"{len(self.game.deck.cards)}", True, self.colors['text_primary'])
            surface.blit(deck_count, (deck_pos[0] + 35, deck_pos[1] + 50))
        else:
            # Show empty deck outline
            pygame.draw.rect(surface, self.colors['table_color'], (deck_pos[0], deck_pos[1], 80, 120), 2)
            empty_text = self.small_font.render("Empty", True, self.colors['text_primary'])
            surface.blit(empty_text, (deck_pos[0] + 20, deck_pos[1] + 50))
        
        # Draw table cards (played cards) in a staggered layout
        if self.game.table_cards:
            # Calculate the base position for the table cards
            base_table_pos = (center_x - 100, center_y - 60)  # Position more centrally
            
            # Show up to the last 8 cards with a staggered layout
            visible_cards = min(8, len(self.game.table_cards))
            start_index = max(0, len(self.game.table_cards) - visible_cards)
            
            # Calculate the offset between cards based on available space
            # Use a different offset pattern to create a "fan" effect
            x_offset = 30  # Horizontal offset between cards
            y_offset = 15  # Vertical offset between cards
            
            # Display the visible cards with staggered layout
            for i in range(start_index, len(self.game.table_cards)):
                card_index = i - start_index  # Relative index within visible cards
                card = self.game.table_cards[i]
                
                # Apply some randomness to the stagger for a more natural look
                random_offset_x = (i % 3) * 5 - 5  # -5, 0, or 5 pixels
                random_offset_y = (i % 2) * 3 - 2  # -2 or 1 pixels
                
                card_pos = (base_table_pos[0] + card_index * x_offset + random_offset_x, 
                            base_table_pos[1] + card_index * y_offset + random_offset_y)
                
                # Special highlighting for cards with effects
                if card.rank in [1, 6, 7, 8]:  # Ace, 6, 7, or 8
                    # Draw a subtle glow around cards with special effects
                    effect_colors = {
                        1: (120, 120, 255, 120),  # Blue glow for Aces
                        6: (255, 200, 100, 120),  # Warm yellow glow for 6s
                        7: (120, 255, 120, 120),  # Green glow for 7s
                        8: (255, 120, 120, 120)   # Warm red glow for 8s
                    }
                    
                    # Create a surface for the glow effect
                    glow = pygame.Surface((90, 130), pygame.SRCALPHA)
                    pygame.draw.rect(glow, effect_colors[card.rank], (0, 0, 90, 130), 0, 10)
                    surface.blit(glow, (card_pos[0] - 5, card_pos[1] - 5))
                
                self.card_renderer.render_card(card, card_pos)
            
            # Show total count of cards on the table if there are hidden cards
            if len(self.game.table_cards) > visible_cards:
                hidden_count = len(self.game.table_cards) - visible_cards
                count_text = self.font.render(f"+{hidden_count} more", True, self.colors['text_highlight'])
                count_pos = (base_table_pos[0], base_table_pos[1] - 30)
                surface.blit(count_text, count_pos)
        
        # Draw the human player's cards at the bottom
        human_player = self.game.players[0]
        text = self.font.render("You", True, self.colors['text_primary'])
        text_rect = text.get_rect(center=(center_x, screen_height * 0.92))
        surface.blit(text, text_rect)
        
        # Draw effect indicator for human player if affected by card effects
        if self.player_effect_indicators[0]:
            effect = self.player_effect_indicators[0]
            if effect == "skip_turn":
                indicator_text = "⚠ SKIP TURN"
                color = self.colors['text_error']
            elif effect.startswith("draw_"):
                draw_count = effect.split("_")[1]
                indicator_text = f"⚠ DRAW {draw_count}"
                color = self.colors['text_warning']
            else:
                indicator_text = "⚠ CARD EFFECTS"
                color = self.colors['text_error']
                
            indicator_surface = self.small_font.render(indicator_text, True, color)
            indicator_rect = indicator_surface.get_rect()
            indicator_rect.centerx = center_x
            indicator_rect.bottom = text_rect.top - 5
            
            # Draw background for indicator
            padding = 5
            bg_rect = pygame.Rect(indicator_rect.x - padding, indicator_rect.y - padding, 
                                indicator_rect.width + padding*2, indicator_rect.height + padding*2)
            bg_color = (80, 40, 20) if effect.startswith("draw_") else (120, 20, 20)
            pygame.draw.rect(surface, bg_color, bg_rect)
            pygame.draw.rect(surface, color, bg_rect, 2)
            
            surface.blit(indicator_surface, indicator_rect)
        
        # Draw and highlight the human player's cards
        human_card_start_x = center_x - (len(human_player.hand) * 45)  # Center cards
        human_card_y = screen_height * 0.75  # Position cards at 75% of screen height
        
        for j, card in enumerate(human_player.hand):
            card_pos = (human_card_start_x + j * 90, human_card_y)
            
            # Highlight staged cards with warm colors
            if j in self.staged_cards:
                # Make staged cards move up slightly
                card_pos = (card_pos[0], card_pos[1] - 20)
                # Staged cards (golden yellow)
                pygame.draw.rect(surface, self.colors['card_select_primary'], 
                              (card_pos[0] - 5, card_pos[1] - 5, 90, 130), 3)
            
            # Draw a subtle indicator for playable cards
            elif self.game.can_play_card(card) and not self.game.must_draw:
                # Warm green indicator for playable cards
                pygame.draw.rect(surface, self.colors['card_playable'], 
                              (card_pos[0] - 2, card_pos[1] - 2, 84, 124), 2)
            
            # Draw the card facing up
            self.card_renderer.render_card(card, card_pos)

    def handle_events(self, event):
        """Handle events for the game screen"""
        if event.type == pygame.KEYDOWN:
            # Handle keys for toggling fullscreen mode
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F11:
                # Toggle fullscreen mode
                pygame.display.toggle_fullscreen()
                
            # Add keyboard shortcuts for game actions
            if self.game.is_running and self.game.is_human_turn:
                # D key for drawing cards
                if event.key == pygame.K_d and not self.show_new_round_button:
                    self.draw_card()
                    
                # F key for finishing turn with staged cards
                elif event.key == pygame.K_f and not self.show_new_round_button:
                    self.finish_turn()
                    
                # C key for clearing staged cards
                elif event.key == pygame.K_c and not self.show_new_round_button:
                    self.clear_staged_cards()
                    
                # A key for staging all cards of the same rank
                elif event.key == pygame.K_a and not self.show_new_round_button:
                    # Get the first staged card or prompt user to select a card
                    if self.staged_cards:
                        self.stage_all_same_rank(self.staged_cards[0])
                    else:
                        self.set_message("Select a card first before using 'A' to stage all of the same rank")
                    
                # Number keys 1-9 for staging cards (0 would be 10th card)
                if event.key in range(pygame.K_1, pygame.K_9 + 1) and not self.show_new_round_button:
                    card_index = event.key - pygame.K_1  # Convert to 0-based index
                    if card_index < len(self.game.players[0].hand):
                        self.stage_card(card_index)
                        
            # N key for next round when available
            if event.key == pygame.K_n and self.show_new_round_button:
                self.start_new_round()
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle suit selection buttons first (highest priority)
            if self.waiting_for_suit_choice:
                mouse_pos = pygame.mouse.get_pos()
                for rect, suit, name, color in self.suit_buttons:
                    if rect.collidepoint(mouse_pos):
                        # Player chose a suit for the Jack
                        human_player = self.game.players[0]
                        
                        # Store the chosen suit and finish the turn
                        self.pending_suit_choice = suit
                        
                        # Get the cards that were staged as Jacks
                        cards_to_play = [human_player.hand[i] for i in self.jack_indices]
                        card_info = ", ".join([card.get_card_info() for card in cards_to_play])
                        
                        # Play the Jack(s) with the chosen suit using the game's play_cards method
                        if not self.game.play_cards(human_player, self.jack_indices, suit):
                            self.set_message(f"Failed to play {card_info}")
                        else:
                            self.set_message(f"Played {card_info} and chose {name}")
                        
                        # Reset the selection state
                        self.waiting_for_suit_choice = False
                        self.jack_indices = []
                        self.staged_cards = []
                        self.suit_buttons = []
                        
                        # Clear pending suit choice
                        if hasattr(self, 'pending_suit_choice'):
                            delattr(self, 'pending_suit_choice')
                        
                        # End the human player's turn
                        self.game.end_player_turn()
                        
                        # Check for win condition
                        if len(human_player.hand) == 0:
                            self.set_message("You win!")
                            self.show_new_round_button = True
                        else:
                            # Let the AI take its turn
                            self.process_ai_turns()
                        return
                        
            # Handle button clicks
            for i, button in enumerate(self.buttons):
                if button.is_clicked():
                    # If player must draw, only allow Draw Card button (index 0) and End Game button (index 3)
                    if self.game.must_draw and i != 0 and i != 3:
                        self.error_message = "You must draw a card!"
                        self.error_time = pygame.time.get_ticks()
                        continue
                    
                    # If player has already used their optional draw, prevent another draw (except when covering 6)
                    if i == 0 and self.game.optional_draw_used and not self.game.must_draw:  # Draw Card button
                        # Allow drawing if covering a 6 and no valid cards
                        if not (self.game.pending_effects['requires_six'] and not self.game.has_valid_play(self.game.players[0])):
                            self.error_message = "You can only draw one optional card per turn."
                            self.error_time = pygame.time.get_ticks()
                            continue
                    
                    # If player is trying to draw but has a card to cover a 6
                    if i == 0 and self.game.pending_effects['requires_six'] and self.game.has_valid_play(self.game.players[0]) and not self.game.must_draw:
                        self.error_message = "You already have a card that can cover the 6. You must play it."
                        self.error_time = pygame.time.get_ticks()
                        continue
                    
                    button.click()
            
            # Handle Next Round button if shown
            if self.show_new_round_button and self.new_round_button.is_clicked():
                self.new_round_button.click()
            
            # Handle card clicking (to stage cards)
            if self.game.is_human_turn and not self.game.must_draw and self.game.is_running and not self.waiting_for_suit_choice:
                human_player = self.game.players[0]
                # Use game area width (excluding info panel) to match drawing coordinates
                screen_width = self.game_area_width
                screen_height = self.screen.get_height()
                center_x = screen_width // 2
                human_card_start_x = center_x - (len(human_player.hand) * 45)  # Center cards
                human_card_y = screen_height * 0.75  # Position cards at 75% of screen height
                
                # Track if any card was clicked
                card_clicked = False
                
                for i in range(len(human_player.hand)):
                    card_pos = (human_card_start_x + i * 90, human_card_y)
                    card_rect = pygame.Rect(card_pos[0], card_pos[1], 80, 120)
                    
                    # Check for raised cards (staged cards)
                    if i in self.staged_cards:
                        raised_rect = pygame.Rect(card_pos[0], card_pos[1] - 20, 80, 120)
                        if raised_rect.collidepoint(pygame.mouse.get_pos()):
                            # Clicked an already-staged card - unstage it
                            card_clicked = True
                            self.staged_cards.remove(i)
                            self.set_message(f"Unstaged {human_player.hand[i].get_card_info()}")
                            break  # Exit after handling the raised card click
                    
                    if card_rect.collidepoint(pygame.mouse.get_pos()):
                        # Clicked a card - attempt to stage it
                        card_clicked = True
                        self.stage_card(i)
                        break  # Exit the loop after handling the clicked card
    
    def update(self):
        """Update game state"""
        # Check for game over
        if self.game.is_running:
            self.game.check_round_over()
            
            # Check if computer is choosing a suit and trigger visual indicator
            if self.game.pending_effects['computer_choosing_suit'] and not self.computer_choosing_suit:
                self.start_computer_suit_selection()
                # Reset the game flag to avoid triggering multiple times
                self.game.pending_effects['computer_choosing_suit'] = False
            
            # Check if human player has no valid plays but hasn't been told to draw yet
            if self.game.is_human_turn and not self.game.must_draw:
                human_player = self.game.players[0]
                if not self.game.has_valid_play(human_player) and len(self.game.deck.cards) > 0:
                    self.game.must_draw = True
                    self.error_message = "You have no valid cards to play - you must draw!"
                    self.error_time = pygame.time.get_ticks()
                elif not self.game.optional_draw_used and len(self.game.deck.cards) > 0 and pygame.time.get_ticks() - self.error_time > 3000:
                    # Remind player they can draw an optional card (after any other error message has cleared)
                    self.error_message = "Remember: You can draw one optional card this turn."
                    self.error_time = pygame.time.get_ticks()
            
            # Check if round is over but game should continue
            if not self.game.is_running and self.game.round_end_message:
                if "Game Over!" not in self.game.round_end_message:
                    # This round is over but the game should continue
                    self.show_new_round_button = True
    
    def on_enter(self):
        """Called when this screen becomes active"""
        # Make sure the game is running
        self.game.is_running = True
        self.staged_cards = []         # Clear staged cards
        self.error_message = None      # Clear any error messages
        self.game.must_draw = False    # Reset draw flag
        self.show_new_round_button = False
        
        # Check if human player needs to draw immediately at game start
        if self.game.is_human_turn:
            human_player = self.game.players[0]
            if not self.game.has_valid_play(human_player) and len(self.game.deck.cards) > 0:
                self.game.must_draw = True
                self.error_message = "You have no valid cards to play - you must draw!"
                self.error_time = pygame.time.get_ticks()

    def show_game_over(self, surface):
        """Display game over or round over message"""
        # Get current screen dimensions
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        if self.game.round_end_message:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            surface.blit(overlay, (0, 0))
            
            # Create a message box - scale with screen size
            box_width = min(screen_width * 0.7, 800)
            box_height = min(screen_height * 0.4, 300)
            message_box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            message_box.fill((50, 50, 50, 230))
            box_rect = message_box.get_rect(center=(center_x, center_y))
            surface.blit(message_box, box_rect.topleft)
            
            # Draw border around the box
            pygame.draw.rect(surface, (255, 215, 0), box_rect, 3)
            
            # Show the round end message - may need to split into multiple lines
            big_font_size = min(int(screen_height * 0.08), 60)
            big_font = pygame.font.Font(None, big_font_size)
            
            if "Game Over!" in self.game.round_end_message:
                # Game is completely over
                header = big_font.render("Game Over!", True, (255, 0, 0))
                header_rect = header.get_rect(center=(center_x, center_y - box_height * 0.25))
                surface.blit(header, header_rect)
                
                # Split the rest of the message
                message_parts = self.game.round_end_message.split("Game Over! ")[1].split(". ")
                for i, part in enumerate(message_parts):
                    text = self.font.render(part, True, (255, 255, 255))
                    text_rect = text.get_rect(center=(center_x, center_y + i * 40))
                    surface.blit(text, text_rect)
                
                # Show final instruction
                restart_text = self.font.render("Press 'End Game' to return to menu", True, (255, 255, 255))
                restart_rect = restart_text.get_rect(center=(center_x, center_y + box_height * 0.25))
                surface.blit(restart_text, restart_rect)
            else:
                # Just a round end
                header = big_font.render(f"Round {self.game.round_number} Complete!", True, (255, 215, 0))
                header_rect = header.get_rect(center=(center_x, center_y - box_height * 0.25))
                surface.blit(header, header_rect)
                
                # Split the message by sentences
                message_parts = self.game.round_end_message.split(". ")
                for i, part in enumerate(message_parts):
                    if part and i < 3:  # Limit to 3 lines to avoid overflow
                        text = self.font.render(part, True, (255, 255, 255))
                        text_rect = text.get_rect(center=(center_x, center_y + i * 40))
                        surface.blit(text, text_rect)
                
                # If Next Round button is showing, add instructions
                if self.show_new_round_button:
                    next_round_text = self.font.render("Press 'Next Round' to continue", True, (255, 255, 0))
                    next_rect = next_round_text.get_rect(center=(center_x, center_y + box_height * 0.25))
                    surface.blit(next_round_text, next_rect)
        elif not self.game.is_running:
            # Fallback for old game over behavior
            # Create a semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            surface.blit(overlay, (0, 0))
            
            # Determine winner
            human_player = self.game.players[0]
            computer_player = self.game.players[1]
            
            if len(human_player.hand) == 0:
                winner_text = "You Win!"
                color = (0, 255, 0)  # Green for win
            elif len(computer_player.hand) == 0:
                winner_text = "Computer Wins!"
                color = (255, 0, 0)  # Red for loss
            else:
                winner_text = "Game Over"
                color = (255, 255, 255)  # White for tie or other
            
            # Create a large font for game over text
            big_font_size = min(int(screen_height * 0.12), 80)
            big_font = pygame.font.Font(None, big_font_size)
            text = big_font.render(winner_text, True, color)
            text_rect = text.get_rect(center=(center_x, center_y))
            surface.blit(text, text_rect)
            
            # Add "Play Again" instruction
            restart_text = self.font.render("Press 'End Game' to return to menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(center_x, center_y + screen_height * 0.1))
            surface.blit(restart_text, restart_rect)

    def display_error_message(self, surface):
        """Display an error message for invalid moves"""
        if self.error_message:
            # Get screen dimensions
            screen_width = surface.get_width()
            screen_height = surface.get_height()
            
            # Display the message for 3 seconds (3000ms)
            current_time = pygame.time.get_ticks()
            if current_time - self.error_time < 3000:
                # Calculate error message dimensions based on screen size
                error_width = min(screen_width * 0.6, 600)
                error_height = min(screen_height * 0.06, 50)
                
                # Create a semi-transparent background for the error
                error_bg = pygame.Surface((error_width, error_height), pygame.SRCALPHA)
                error_bg.fill((255, 0, 0, 180))  # Semi-transparent red
                
                # Position at the top center of the screen
                bg_rect = error_bg.get_rect(center=(screen_width / 2, screen_height * 0.2))
                surface.blit(error_bg, bg_rect.topleft)
                
                # Render the error text
                error_text = self.font.render(self.error_message, True, (255, 255, 255))
                text_rect = error_text.get_rect(center=(screen_width / 2, screen_height * 0.2))
                surface.blit(error_text, text_rect)
            else:
                # Clear the error after the time expires
                self.error_message = None

    def display_special_card_rules(self, surface, screen_width, y_pos):
        """Display the special card rules in a compact format"""
        rule_spacing = 22  # Spacing between rules
        
        # Display special card rules with color coding
        rules = [
            ("8s", "Next player draws 2 cards & skips turn", (255, 100, 100)),  # Red
            ("7s", "Next player draws 1 card", (100, 255, 100)),  # Green
            ("Aces", "Next player skips turn", (100, 100, 255)),  # Blue
            ("6s", "Must be covered by same player with same suit as the most recent 6 or another 6", (255, 255, 100)),  # Yellow
            ("Draw", "You can draw 1 optional card per turn", (200, 200, 200))  # White
        ]
        
        # Create a semi-transparent background for rules
        rules_width = screen_width * 0.9
        rules_height = len(rules) * rule_spacing + 15
        rules_bg = pygame.Surface((rules_width, rules_height), pygame.SRCALPHA)
        rules_bg.fill((0, 0, 0, 80))  # Semi-transparent black
        
        surface.blit(rules_bg, (screen_width/2 - rules_width/2, y_pos - 5))
        
        # Display each rule
        for i, (card, rule, color) in enumerate(rules):
            # Create text with highlighted card name
            card_text = self.small_font.render(card + ":", True, color)
            rule_text = self.small_font.render(rule, True, (200, 200, 200))
            
            # Position and render
            y = y_pos + i * rule_spacing
            surface.blit(card_text, (screen_width * 0.15, y))
            surface.blit(rule_text, (screen_width * 0.25, y))

    def create_suit_selection_buttons(self):
        """Create suit selection buttons when a Jack is played"""
        # Center of the screen
        center_x = self.screen_width / 2
        center_y = self.screen_height / 2
        
        # Dimensions and spacing
        button_width = 120
        button_height = 150
        spacing = 30
        
        # Calculate positions for 4 suit buttons in a horizontal row
        suits = [
            ('H', "Hearts", (255, 80, 80)),    # Red
            ('D', "Diamonds", (255, 150, 80)), # Orange
            ('C', "Clubs", (80, 200, 80)),     # Green
            ('S', "Spades", (80, 80, 255))     # Blue
        ]
        
        total_width = len(suits) * button_width + (len(suits) - 1) * spacing
        start_x = center_x - total_width / 2
        
        # Create buttons - store rect, suit value, name, and color
        self.suit_buttons = []
        for i, (suit, name, color) in enumerate(suits):
            x = start_x + i * (button_width + spacing)
            y = center_y - button_height / 2
            rect = pygame.Rect(x, y, button_width, button_height)
            self.suit_buttons.append((rect, suit, name, color))

    def draw_suit_selection(self, surface):
        """Draw the suit selection interface when a Jack is played"""
        if not self.waiting_for_suit_choice or not self.suit_buttons:
            return
        
        # Dim the background with a semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        surface.blit(overlay, (0, 0))
        
        # Draw title text
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Choose a Suit", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width / 2, self.screen_height / 2 - 120))
        surface.blit(title, title_rect)
        
        # Draw suit buttons
        for rect, suit, name, color in self.suit_buttons:
            # Draw button background
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 3)  # White border
            
            # Draw suit name
            font = pygame.font.Font(None, 36)
            text = font.render(name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(rect.centerx, rect.centery + 30))
            surface.blit(text, text_rect)
            
            # Draw suit symbol
            symbol_font = pygame.font.Font(None, 80)
            symbol_map = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}
            symbol = symbol_font.render(symbol_map[suit], True, (255, 255, 255))
            symbol_rect = symbol.get_rect(center=(rect.centerx, rect.centery - 20))
            surface.blit(symbol, symbol_rect)

    def start_computer_suit_selection(self):
        """Start the visual indicator for computer suit selection"""
        self.computer_choosing_suit = True
        self.computer_choice_start_time = pygame.time.get_ticks()

    def draw_computer_choosing_suit(self, surface):
        """Draw a visual indicator when the computer is choosing a suit"""
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.computer_choice_start_time
        
        # Create a pulsing effect
        pulse = (math.sin(elapsed_time * 0.005) + 1) * 0.5
        
        # Calculate coordinates for the indicator (center of screen)
        screen_center_x = self.game_area_x + (self.game_area_width // 2)
        screen_center_y = self.screen_height // 2 - 50
        
        # Background glow with pulsing intensity
        glow_radius = 120
        glow_color = (255, int(100 + pulse * 155), 0, int(50 + pulse * 150))
        
        # Create a surface with alpha for the glow
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
        
        # Draw the glow centered on the indicator position
        surface.blit(glow_surface, (screen_center_x - glow_radius, screen_center_y - glow_radius))
        
        # Draw the text
        font = pygame.font.Font(None, 42)
        text_color = (255, 255, 255)
        text = font.render("Computer choosing suit...", True, text_color)
        text_rect = text.get_rect(center=(screen_center_x, screen_center_y))
        surface.blit(text, text_rect)
        
        # Draw dots for "waiting" animation
        dot_count = (elapsed_time // 500) % 4  # 0-3 dots based on time
        dots = "." * dot_count
        dots_text = font.render(dots, True, text_color)
        dots_rect = dots_text.get_rect(topleft=(text_rect.right + 5, text_rect.top))
        surface.blit(dots_text, dots_rect)

    def stage_all_same_rank(self, card_index):
        """Stage all cards of the same rank as the selected card"""
        # Get the player's hand
        human_player = self.game.players[0]
        selected_card = human_player.hand[card_index]
        
        # Clear any previously staged cards
        self.clear_staged_cards()
        
        # Find all cards with the same rank that can be played
        same_rank_indices = []
        for i, card in enumerate(human_player.hand):
            if card.rank == selected_card.rank and self.game.can_play_card(card):
                same_rank_indices.append(i)
        
        # Stage all found cards
        if same_rank_indices:
            self.staged_cards = same_rank_indices
            card_count = len(same_rank_indices)
            self.set_message(f"Staged {card_count} cards of rank {selected_card.rank}")
            return True
        else:
            self.set_message(f"No playable cards of rank {selected_card.rank}")
            return False
    
    def draw_card(self):
        """Draw a card from the deck for the human player"""
        if not self.game.is_running or not self.game.is_human_turn:
            return
            
        # Special case: If covering a 6 and player has no valid cards, allow multiple draws
        if self.game.pending_effects['requires_six'] and not self.game.has_valid_play(self.game.players[0]):
            self.draw_card_for_six_covering()
            return
            
        # If already drawn the optional card this turn, prevent drawing again unless required
        if self.game.optional_draw_used and not self.game.must_draw:
            self.set_message("You have already drawn your optional card this turn")
            return
            
        # Draw a card for the human player
        human_player = self.game.players[0]
        if len(self.game.deck.cards) > 0:
            card = self.game.deck.draw_card()
            human_player.hand.append(card)
            
            # Reset any error messages
            self.error_message = None
            
            # Log the draw
            self.set_message(f"You drew {card.get_card_info()}")
            
            # Mark that the player has used their optional draw
            # or clear the must_draw flag if they were required to draw
            if self.game.must_draw:
                self.game.must_draw = False
            else:
                self.game.optional_draw_used = True
            
            # Check if the card drawn can be immediately played on a 6
            if self.game.pending_effects['requires_six'] and self.game.can_play_card(card):
                self.set_message(f"You drew {card.get_card_info()} which can be played on the 6")
        else:
            self.set_message("The deck is empty!")
            
    def draw_card_for_six_covering(self):
        """Draw a card specifically for covering a 6 - allows multiple draws"""
        human_player = self.game.players[0]
        
        # Check if deck is empty
        if len(self.game.deck.cards) == 0:
            # Try to reshuffle
            if self.game.reshuffle_table_cards():
                self.set_message("Deck was empty! Cards reshuffled.")
            else:
                self.set_message("Deck is empty and cannot reshuffle! You cannot cover the 6.")
                return
        
        # Draw a card
        card = self.game.deck.draw_card()
        if card:
            human_player.hand.append(card)
            
            # Reset any error messages
            self.error_message = None
            
            # Check if this card can cover the 6
            if self.game.can_play_card(card):
                self.set_message(f"You drew {card.get_card_info()} which can cover the 6!")
            else:
                self.set_message(f"You drew {card.get_card_info()}, but it cannot cover the 6. Draw again or pass turn.")
        else:
            self.set_message("Failed to draw a card!")
            
    def start_new_round(self):
        """Start a new round of the game"""
        self.game.start_new_round()
        self.show_new_round_button = False
        # Clear all player effect indicators when starting a new round
        self.player_effect_indicators = {0: None, 1: None}
        self.set_message(f"Starting round {self.game.round_number}")
        
    def quit_game(self):
        """End the current game and return to menu"""
        self.game.is_running = False
        self.game.round_end_message = None  # Clear any round end message
        return "return_to_menu"
    
    def draw_message_log(self, surface):
        """Draw a message log window on the left side of the screen"""
        # Draw panel background
        panel_rect = pygame.Rect(0, 0, self.message_panel_width, self.screen_height)
        pygame.draw.rect(surface, self.colors['message_log_bg'], panel_rect)
        pygame.draw.rect(surface, self.colors['panel_border'], panel_rect, 3)
        
        # Draw title
        title = self.font.render("Game Messages", True, self.colors['text_highlight'])
        title_rect = title.get_rect(centerx=self.message_panel_width//2, y=15)
        surface.blit(title, title_rect)
        
        # Draw divider line
        pygame.draw.line(surface, 
                       self.colors['panel_border'],
                       (10, title_rect.bottom + 10), 
                       (self.message_panel_width - 10, title_rect.bottom + 10), 
                       2)
        
        # Get messages and render them
        messages = get_messages()
        
        # Starting position for first message
        y_pos = title_rect.bottom + 30
        available_height = self.screen_height - y_pos - 20  # 20px bottom margin
        max_visible_messages = min(len(messages), 15)  # Limit visible messages
        
        # If we have more messages than can fit, show the most recent ones
        start_index = max(0, len(messages) - max_visible_messages)
        messages_to_show = messages[start_index:]
        
        # Draw each message
        for i, msg in enumerate(messages_to_show):
            # Wrap text if it's too long
            words = msg.split()
            wrapped_lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                # Check if adding this word would make the line too long
                if self.small_font.size(test_line)[0] < self.message_panel_width - 30:
                    current_line = test_line
                else:
                    wrapped_lines.append(current_line)
                    current_line = word
            
            # Add the last line
            if current_line:
                wrapped_lines.append(current_line)
            
            # Render each line of the wrapped message
            for line in wrapped_lines:
                text_surface = self.small_font.render(line, True, self.colors['message_text'])
                surface.blit(text_surface, (15, y_pos))
                y_pos += 20
            
            # Add a small gap between messages
            y_pos += 5
            
            # If we're going to exceed the available height, stop rendering
            if y_pos > self.screen_height - 20:
                break
                
    def draw_info_panel(self, surface):
        """Draw information panel on the right side"""
        # Draw panel background
        panel_rect = pygame.Rect(self.info_panel_x, 0, self.info_panel_width, self.screen_height)
        pygame.draw.rect(surface, self.colors['bg_panel'], panel_rect)
        pygame.draw.rect(surface, self.colors['panel_border'], panel_rect, 3)
        
        # Draw title
        title = self.font.render("Game Information", True, self.colors['text_highlight'])
        title_rect = title.get_rect(centerx=self.info_panel_x + self.info_panel_width//2, y=15)
        surface.blit(title, title_rect)
        
        # Draw divider line
        pygame.draw.line(surface, 
                       self.colors['panel_border'],
                       (self.info_panel_x + 10, title_rect.bottom + 10), 
                       (self.info_panel_x + self.info_panel_width - 10, title_rect.bottom + 10), 
                       2)
        
        # Starting y position for info content
        y_pos = title_rect.bottom + 30
        center_x = self.info_panel_x + self.info_panel_width // 2
        
        # -- Display round information --
        round_text = self.font.render(f"Round: {self.game.round_number}", True, self.colors['text_primary'])
        round_rect = round_text.get_rect(centerx=center_x, y=y_pos)
        surface.blit(round_text, round_rect)
        y_pos += round_rect.height + 20
        
        # -- Display player hand sizes --
        human_player = self.game.players[0]
        computer_player = self.game.players[1]
        
        # Player cards
        player_text = self.font.render(f"Your cards: {len(human_player.hand)}", True, self.colors['text_primary'])
        player_rect = player_text.get_rect(centerx=center_x, y=y_pos)
        surface.blit(player_text, player_rect)
        y_pos += player_rect.height + 10
        
        # Computer cards
        comp_text = self.font.render(f"Computer cards: {len(computer_player.hand)}", True, self.colors['text_primary'])
        comp_rect = comp_text.get_rect(centerx=center_x, y=y_pos)
        surface.blit(comp_text, comp_rect)
        y_pos += comp_rect.height + 10
        
        # Deck cards
        deck_text = self.font.render(f"Cards in deck: {len(self.game.deck.cards)}", True, self.colors['text_primary'])
        deck_rect = deck_text.get_rect(centerx=center_x, y=y_pos)
        surface.blit(deck_text, deck_rect)
        y_pos += deck_rect.height + 30
        
        # -- Display current turn --
        turn_text = "Your Turn" if self.game.is_human_turn else "Computer's Turn"
        turn_color = self.colors['text_success'] if self.game.is_human_turn else self.colors['text_warning']
        
        turn_label = self.font.render("Current Turn:", True, self.colors['text_secondary'])
        turn_label_rect = turn_label.get_rect(centerx=center_x, y=y_pos)
        surface.blit(turn_label, turn_label_rect)
        y_pos += turn_label_rect.height + 5
        
        turn_value = self.font.render(turn_text, True, turn_color)
        turn_value_rect = turn_value.get_rect(centerx=center_x, y=y_pos)
        surface.blit(turn_value, turn_value_rect)
        y_pos += turn_value_rect.height + 30
        
        # -- Display any active effects --
        effects_label = self.font.render("Active Effects:", True, self.colors['text_secondary'])
        effects_label_rect = effects_label.get_rect(centerx=center_x, y=y_pos)
        surface.blit(effects_label, effects_label_rect)
        y_pos += effects_label_rect.height + 10
        
        # List of active effects
        active_effects = []
        
        if self.game.pending_effects['draw_cards'] > 0:
            active_effects.append(f"Draw {self.game.pending_effects['draw_cards']} cards")
            
        if self.game.pending_effects['skip_turn']:
            active_effects.append("Skip next turn")
            
        if self.game.pending_effects['requires_six']:
            six_player_name = "You" if self.game.pending_effects['six_player'] == self.game.players[0] else "Computer"
            six_suit = self.game.pending_effects['six_suit']
            suit_name = self.game.get_suit_name(six_suit) if six_suit else "Unknown"
            active_effects.append(f"{six_player_name} must cover 6 ({suit_name})")
            
        if self.game.pending_effects['suit_enforced']:
            suit_name = self.game.get_suit_name(self.game.pending_effects['chosen_suit'])
            active_effects.append(f"Suit enforced: {suit_name}")
            
        if not active_effects:
            active_effects.append("None")
            
        # Display each effect
        for effect in active_effects:
            effect_text = self.small_font.render(f"• {effect}", True, self.colors['text_primary'])
            effect_rect = effect_text.get_rect(x=self.info_panel_x + 30, y=y_pos)
            surface.blit(effect_text, effect_rect)
            y_pos += effect_rect.height + 5
            
        y_pos += 20
        
        # -- Display error messages if any --
        self.display_error_message(surface)
        
        # -- Display card rules at the bottom --
        rules_y = self.screen_height - 150
        self.display_special_card_rules(surface, self.info_panel_width, rules_y)

    def process_ai_turns(self):
        """Process AI turns until it's the human player's turn again or game ends"""
        if not self.game.is_running:
            return
            
        # Process AI turns until it's human's turn again or game ends
        while not self.game.is_human_turn and self.game.is_running:
            # Let the AI play
            self.game.process_computer_turn()
            
            # Check for win condition after AI plays
            computer_player = self.game.players[1]
            if len(computer_player.hand) == 0:
                self.set_message("Computer wins!")
                self.show_new_round_button = True
                break

    def set_player_effect_indicator(self, player_index, effect_type):
        """Set an effect indicator for a player when they're affected by card effects"""
        self.player_effect_indicators[player_index] = effect_type
        
    def clear_player_effect_indicator(self, player_index):
        """Clear the effect indicator for a player when it's their turn again"""
        self.player_effect_indicators[player_index] = None

    def on_player_effect_notification(self, player_index, effect_type, duration):
        """Callback method to handle player effect notifications from the game"""
        if effect_type:
            self.set_player_effect_indicator(player_index, effect_type)
        else:
            self.clear_player_effect_indicator(player_index)