from .deck import Deck
from .player import Player
import sys
import random

def display_message(message):
    """Display a message to the user."""
    print(message)

class Game:
    def __init__(self):
        self.players = []
        self.deck = None
        self.is_running = False
        self.current_player_index = 0
        self.table_cards = []  # Cards placed on the table
        self.is_human_turn = True  # True for human player, False for computer
        self.must_draw = False  # Flag to indicate when the human player must draw
        self.optional_draw_used = False  # Flag to track if the player has used their optional draw
        self.point_multiplier = 1  # Point multiplier increases with each reshuffle
        self.round_number = 1  # Track the current round number
        self.round_end_message = None  # Message to display when a round ends
        
        # Callback for notifying GUI of player effects
        self.on_player_effect_callback = None

        self.pending_effects = {
            'draw_cards': 0,     # Number of cards to draw (for 8s and 7s)
            'skip_turn': False,  # Whether the next player should skip a turn (for Aces and 8s)
            'requires_six': False,  # Whether the next card must be a 6 or suit match
            'six_chain': 0,      # Track how many 6s have been played in sequence
            'six_player': None,   # Track which player played the 6 (to enforce same-player rule)
            'six_suit': None,    # Track the suit of the most recent 6 that needs to be covered
            'chosen_suit': None,  # Track the suit chosen after a Jack is played
            'suit_enforced': False,  # Flag to indicate if a specific suit is being enforced
            'computer_choosing_suit': False  # Flag for visual indicator when computer chooses suit
        }

    def create_deck(self):
        """Create and return a shuffled deck"""
        deck = Deck()
        deck.shuffle()
        return deck

    def start_game(self):
        """Start the game with human vs computer"""
        self.is_running = True
        self.current_player_index = 0
        self.is_human_turn = True
        if not self.deck:
            self.deck = self.create_deck()
        
        # Make sure we have exactly 2 players: human and computer
        self.players = [
            Player("Player"),  # Human player
            Player("Computer")  # Computer player
        ]
        
        self._deal_initial_cards()

    def start_new_round(self):
        """Start a new round of the game"""
        self.round_number += 1
        self.table_cards = []
        self.is_human_turn = True
        self.current_player_index = 0
        self.must_draw = False
        self.optional_draw_used = False
        self.point_multiplier = 1
        
        # Reset all pending effects
        self.pending_effects = {
            'draw_cards': 0,
            'skip_turn': False,
            'requires_six': False,
            'six_chain': 0,
            'six_player': None,
            'six_suit': None,
            'chosen_suit': None,
            'suit_enforced': False,
            'computer_choosing_suit': False
        }
        
        # Create a fresh deck
        self.deck = self.create_deck()
        
        # Clear players' hands but keep their points
        for player in self.players:
            player.hand = []
        
        # Deal cards for the new round
        self._deal_initial_cards()
        
        display_message(f"\nRound {self.round_number} starts!")

    def _deal_initial_cards(self):
        """Deal initial cards to all players"""
        for _ in range(5):  # Deal 5 cards to each player
            for player in self.players:
                card = self.deck.draw_card()
                if card:
                    player.add_card(card)
    
    def play_cards(self, player, card_indices, chosen_suit=None):
        """Place multiple cards of the same rank from the player's hand onto the table"""
        if not card_indices or not all(0 <= idx < len(player.hand) for idx in card_indices):
            return None
        
        # Get all cards but don't remove them yet
        cards_to_play = [player.hand[idx] for idx in sorted(card_indices, reverse=True)]
        
        # Check if all cards have the same rank
        first_rank = cards_to_play[0].rank
        if not all(card.rank == first_rank for card in cards_to_play):
            display_message("All cards played together must be of the same rank")
            return None
        
        # Check if the first card can be played according to the rules
        if self.can_play_card(cards_to_play[0]):
            # Remove and play all cards (in reverse order to keep indices valid)
            played_cards = []
            for idx in sorted(card_indices, reverse=True):
                played_card = player.hand.pop(idx)
                self.table_cards.append(played_card)
                played_cards.append(played_card)
            
            # Display the play
            display_message(f"{player.name} played {len(played_cards)} cards of rank {first_rank}")
            
            # Apply card effects based on the rank of the played cards (multiplied by count)
            # For Jacks, pass the chosen suit
            if not self.apply_card_effects(played_cards[0], player, len(played_cards), chosen_suit):
                # If effect application fails, return all cards to the player's hand
                for card in reversed(played_cards):
                    self.table_cards.pop()
                player.hand.extend(played_cards)
                return None
            
            return played_cards
        return None
    
    def play_card(self, player, card_index):
        """Backwards compatibility method for playing a single card"""
        return self.play_cards(player, [card_index])
        
    def end_player_turn(self):
        """End the current player's turn and switch to the next player"""
        # Handle the end of turn - essentially a wrapper for next_turn
        self.next_turn()
        
    def apply_card_effects(self, card, player, count=1, chosen_suit=None):
        """Apply special effects based on the card(s) that were just played"""
        # Handle suit enforcement reset logic
        if card.rank == 11:  # New Jack played
            # Will set new suit enforcement below
            pass
        elif self.pending_effects['suit_enforced'] and self.pending_effects['chosen_suit']:
            # If a non-Jack card is played and matches the enforced suit, reset enforcement
            if card.suit == self.pending_effects['chosen_suit']:
                self.pending_effects['suit_enforced'] = False
                self.pending_effects['chosen_suit'] = None
                display_message(f"Suit enforcement ended - {player.name} played a matching card")
        
        # Reset six chain if a non-six card was played
        if self.pending_effects['requires_six'] and card.rank != 6:
            # Only the same player can play a non-6 card, and it must match suit
            if player == self.pending_effects['six_player']:
                self.pending_effects['requires_six'] = False
                self.pending_effects['six_chain'] = 0
                self.pending_effects['six_player'] = None
                self.pending_effects['six_suit'] = None
            else:
                # Different player cannot play on a 6 with anything other than continuing their own turn
                self.pending_effects['draw_cards'] += 1
                display_message(f"{player.name} cannot play on opponent's 6 - Must draw a card")
                return False
        
        # Apply effects based on card rank (multiplied by the number of cards played)
        if card.rank == 8:
            # Multiple 8s: Next player draws 2 cards per 8 and skips turn
            self.pending_effects['draw_cards'] += 2 * count
            self.pending_effects['skip_turn'] = True
            display_message(f"Effect: {player.name} played {count} 8s - Next player must draw {2 * count} cards and skip their turn")
            
        elif card.rank == 7:
            # Multiple 7s: Next player draws 1 card per 7
            self.pending_effects['draw_cards'] += count
            display_message(f"Effect: {player.name} played {count} 7s - Next player must draw {count} cards")
            
        elif card.rank == 1:  # Ace
            # Multiple Aces: Next player skips turn and next player plays
            self.pending_effects['skip_turn'] = True
            display_message(f"Effect: {player.name} played {count} Aces - Next player skips their turn")
            
        elif card.rank == 6:
            # Multiple 6s: Must be covered by matching number of 6s or same suit cards from the SAME player during SAME turn
            self.pending_effects['requires_six'] = True
            self.pending_effects['six_chain'] += count
            self.pending_effects['six_player'] = player
            self.pending_effects['six_suit'] = card.suit  # Track the suit of the most recent 6
            display_message(f"Effect: {player.name} played {count} 6s - Only they can cover them during their turn with same suit cards or more 6s")
            
        elif card.rank == 11:  # Jack
            # For Jack, player can choose the next suit
            self.pending_effects['suit_enforced'] = True
            self.pending_effects['chosen_suit'] = chosen_suit if chosen_suit else card.suit
            suit_name = self.get_suit_name(self.pending_effects['chosen_suit'])
            display_message(f"Effect: {player.name} played a Jack and chose {suit_name} as the next suit")
            
        return True
        
    def get_suit_name(self, suit):
        """Convert suit symbol to name"""
        suit_names = {
            'H': 'Hearts',
            'D': 'Diamonds',
            'C': 'Clubs',
            'S': 'Spades'
        }
        return suit_names.get(suit, suit)
        
    def computer_turn(self):
        """Handle the computer's turn - find valid cards to play with enhanced strategy"""
        computer_player = self.players[1]  # Computer is always second player
        
        # Track if this is a continuation of the computer's turn due to playing a 6
        played_any_card = False
        
        while computer_player.hand:
            # Check if computer must cover its own 6 from a previous play in this same turn
            if self.pending_effects['requires_six'] and self.pending_effects['six_player'] == computer_player:
                display_message("Computer must cover its 6 with a same suit card or another 6")
                # Computer MUST play a valid card to cover the 6
                
                # Look for covering cards: same suit as the top card or another 6
                top_card = self.table_cards[-1]
                covering_indices = []
                
                for i, card in enumerate(computer_player.hand):
                    if self.can_play_card(card):  # This will check 6-covering rules
                        covering_indices.append(i)
                
                if covering_indices:
                    # Play the first valid covering card
                    played_cards = self.play_card(computer_player, covering_indices[0])
                    if played_cards:
                        played_any_card = True
                        # If we played another 6, we need to continue covering
                        if played_cards[0].rank == 6:
                            continue  # Loop continues to cover the new 6
                        else:
                            # Successfully covered with a non-6, exit the loop
                            break
                else:
                    # Computer has no valid covering card - this shouldn't happen if game rules are followed
                    display_message("ERROR: Computer cannot cover its 6! This violates game rules.")
                    break
            else:
                # Normal turn logic
                # First check if computer has any valid card to play
                has_valid_card = False
                for card in computer_player.hand:
                    if self.can_play_card(card):
                        has_valid_card = True
                        break
                        
                # If no valid card, draw until a playable card is found
                if not has_valid_card:
                    display_message("Computer has no valid cards to play - drawing from deck...")
                    # Check if we're in a 6-covering scenario
                    if self.pending_effects['requires_six']:
                        success = self.draw_until_six_covered(computer_player)
                    else:
                        success = self.draw_until_playable(computer_player)
                    
                    if not success:
                        # No playable card found and deck is empty, skip turn
                        display_message("Computer couldn't find a playable card after drawing")
                        break
                # Sometimes use an optional draw strategically (50% chance if not already drawn)
                elif not self.optional_draw_used and random.random() < 0.5 and len(self.deck.cards) > 0:
                    # Computer decides to use its optional draw
                    display_message("Computer uses its optional draw")
                    card = self.deck.draw_card()
                    if card:
                        computer_player.add_card(card)
                        display_message(f"Computer drew: {card.get_card_info()}")
                        self.optional_draw_used = True
                
                # Enhanced strategy with multiple card play:
                # First collect all cards by rank for potential multiple plays
                cards_by_rank = {}
                for i, card in enumerate(computer_player.hand):
                    if card.rank not in cards_by_rank:
                        cards_by_rank[card.rank] = []
                    cards_by_rank[card.rank].append(i)
                
                # Priority 1: If we can go out with multiple Jacks, do it for the bonus
                if 11 in cards_by_rank and len(cards_by_rank[11]) == len(computer_player.hand):
                    strategic_suit = self.choose_strategic_suit(computer_player)
                    self.pending_effects['computer_choosing_suit'] = True  # Trigger visual indicator
                    played_cards = self.play_cards(computer_player, cards_by_rank[11], strategic_suit)
                    display_message(f"Computer plays {len(cards_by_rank[11])} Jacks to win with a bonus!")
                    return played_cards
                    
                # Priority 2: Play multiple 8s to force bigger draw and skip
                if 8 in cards_by_rank and self.can_play_card(computer_player.hand[cards_by_rank[8][0]]):
                    played_cards = self.play_cards(computer_player, cards_by_rank[8])
                    display_message(f"Computer plays {len(cards_by_rank[8])} 8s - You must draw {2 * len(cards_by_rank[8])} cards and skip your turn!")
                    return played_cards
                    
                # Priority 3: Play multiple Aces to force skip
                if 1 in cards_by_rank and self.can_play_card(computer_player.hand[cards_by_rank[1][0]]):
                    played_cards = self.play_cards(computer_player, cards_by_rank[1])
                    display_message(f"Computer plays {len(cards_by_rank[1])} Aces - You must skip your turn!")
                    return played_cards
                
                # Priority 4: Play multiple 7s to force draws
                if 7 in cards_by_rank and self.can_play_card(computer_player.hand[cards_by_rank[7][0]]):
                    played_cards = self.play_cards(computer_player, cards_by_rank[7])
                    display_message(f"Computer plays {len(cards_by_rank[7])} 7s - You must draw {len(cards_by_rank[7])} cards!")
                    return played_cards
                
                # Priority 5: Play multiple cards of matching rank if possible
                if self.table_cards:
                    top_card = self.table_cards[-1]
                    if top_card.rank in cards_by_rank and len(cards_by_rank[top_card.rank]) > 1:
                        played_cards = self.play_cards(computer_player, cards_by_rank[top_card.rank])
                        played_any_card = True
                        # If we played 6s, we need to continue to cover them
                        if played_cards and played_cards[0].rank == 6:
                            continue  # Loop continues to handle covering the 6s
                        return played_cards
                
                # Play a 7 if available (forces opponent to draw)
                for i, card in enumerate(computer_player.hand):
                    if card.rank == 7 and self.can_play_card(card):
                        return self.play_card(computer_player, i)
                        
                # If there's a top card on the table, try to match suit first
                if self.table_cards:
                    top_card = self.table_cards[-1]
                    
                    # Try to match suit - but be strategic about 6s
                    for i, card in enumerate(computer_player.hand):
                        if card.suit == top_card.suit and self.can_play_card(card):
                            # Only play a 6 if we can cover it
                            if card.rank == 6:
                                # Check if we can cover this 6
                                can_cover = False
                                for j, cover_card in enumerate(computer_player.hand):
                                    if j != i and (cover_card.rank == 6 or cover_card.suit == card.suit):
                                        can_cover = True
                                        break
                                if not can_cover:
                                    continue  # Skip this 6 if we can't cover it
                            
                            played_cards = self.play_card(computer_player, i)
                            played_any_card = True
                            # If we played a 6, continue to cover it
                            if played_cards and played_cards[0].rank == 6:
                                continue  # Loop continues to handle covering the 6
                            return played_cards
                    
                    # Then try to match rank - but be strategic about 6s
                    for i, card in enumerate(computer_player.hand):
                        if card.rank == top_card.rank and self.can_play_card(card):
                            # Only play a 6 if we can cover it
                            if card.rank == 6:
                                # Check if we can cover this 6
                                can_cover = False
                                for j, cover_card in enumerate(computer_player.hand):
                                    if j != i and (cover_card.rank == 6 or cover_card.suit == card.suit):
                                        can_cover = True
                                        break
                                if not can_cover:
                                    continue  # Skip this 6 if we can't cover it
                            
                            played_cards = self.play_card(computer_player, i)
                            played_any_card = True
                            # If we played a 6, continue to cover it
                            if played_cards and played_cards[0].rank == 6:
                                continue  # Loop continues to handle covering the 6
                            return played_cards
                    
                    # Check if we have a Jack to play
                    for i, card in enumerate(computer_player.hand):
                        if card.rank == 11 and self.can_play_card(card):
                            # Choose the most strategic suit based on what's in the computer's hand
                            strategic_suit = self.choose_strategic_suit(computer_player)
                            self.pending_effects['computer_choosing_suit'] = True  # Trigger visual indicator
                            display_message(f"Computer plays Jack and chooses {self.get_suit_name(strategic_suit)} as the next suit")
                            return self.play_cards(computer_player, [i], strategic_suit)
                    
                    # Fall back to any valid card that's not a 6 (unless we can cover it)
                    for i, card in enumerate(computer_player.hand):
                        if self.can_play_card(card):
                            # Only play a 6 if we can cover it
                            if card.rank == 6:
                                # Check if we can cover this 6
                                can_cover = False
                                for j, cover_card in enumerate(computer_player.hand):
                                    if j != i and (cover_card.rank == 6 or cover_card.suit == card.suit):
                                        can_cover = True
                                        break
                                if not can_cover:
                                    continue  # Skip this 6 if we can't cover it
                            
                            played_cards = self.play_card(computer_player, i)
                            played_any_card = True
                            # If we played a 6, continue to cover it
                            if played_cards and played_cards[0].rank == 6:
                                continue  # Loop continues to handle covering the 6
                            return played_cards
                
                # If we reach here, computer couldn't play any card
                break
        
        # Return the last played card (if any) to maintain compatibility
        return computer_player.hand if played_any_card else None
    
    def next_turn(self):
        """Switch to the next player's turn"""
        # Check if game is over before switching turns
        if self.check_round_over():
            return
            
        # Switch to the next player
        self.is_human_turn = not self.is_human_turn
        self.current_player_index = 0 if self.is_human_turn else 1
        
        # Reset the optional draw flag at the beginning of each turn
        self.optional_draw_used = False
        
        # Clear any effect indicator for the new current player (their turn is starting)
        if self.on_player_effect_callback:
            self.on_player_effect_callback(self.current_player_index, None, 0)
        
        # Get the next player
        next_player = self.players[self.current_player_index]
        
        # Apply any pending effects from previous card plays
        skip_needed = False
        
        # Handle forced card draws
        if self.pending_effects['draw_cards'] > 0:
            # Force the player to draw cards
            cards_to_draw = self.pending_effects['draw_cards']
            display_message(f"{next_player.name} must draw {cards_to_draw} cards due to card effects")
            
            # Notify GUI that this player is affected by card effects (draw effect)
            if self.on_player_effect_callback:
                self.on_player_effect_callback(self.current_player_index, f"draw_{cards_to_draw}", 3000)  # Show for 3 seconds
            
            # Draw the required cards
            for _ in range(cards_to_draw):
                if len(self.deck.cards) > 0 or self.reshuffle_table_cards():
                    card = self.deck.draw_card()
                    if card:
                        next_player.add_card(card)
                        display_message(f"{next_player.name} drew: {card.get_card_info()}")
                else:
                    display_message(f"Deck is empty! {next_player.name} couldn't draw all required cards")
                    break
                    
            # Reset the draw count
            self.pending_effects['draw_cards'] = 0
        
        # Handle skip turn effect
        if self.pending_effects['skip_turn']:
            display_message(f"{next_player.name} must skip their turn due to card effects")
            skip_needed = True
            self.pending_effects['skip_turn'] = False
            
            # Notify GUI that this player is affected by card effects
            if self.on_player_effect_callback:
                self.on_player_effect_callback(self.current_player_index, "skip_turn", 3000)  # Show for 3 seconds
        
        # If player needs to skip their turn, immediately switch to the next player
        if skip_needed:
            display_message(f"Turn passes to the next player")
            # Since this player is skipped, move directly to the next player's turn
            self.is_human_turn = not self.is_human_turn
            self.current_player_index = 0 if self.is_human_turn else 1
            
            # Get the new current player
            next_player = self.players[self.current_player_index]
            display_message(f"It's now {next_player.name}'s turn")
        
        # If it's the computer's turn, let it play automatically
        if not self.is_human_turn:
            # Computer plays its turn
            played_card = self.computer_turn()
            
            # Check if game is over after computer's turn
            if not self.check_round_over():
                # Check if computer played a card that affects the next turn
                if played_card and (self.pending_effects['skip_turn'] or self.pending_effects['draw_cards'] > 0):
                    # If computer played a card with effects, we need another next_turn call
                    # to process these effects for the human player
                    display_message("Computer played a special card with effects")
                    return self.next_turn()
                
                # Then switch back to human if not skipped
                self.is_human_turn = True
                self.current_player_index = 0
                
                # Check if human player has any valid cards
                human_player = self.players[0]
                if not self.has_valid_play(human_player) and len(self.deck.cards) > 0:
                    # Signal that human must draw (handled in UI)
                    display_message("You have no valid cards to play - you must draw from the deck")
                    self.must_draw = True
                else:
                    self.must_draw = False

    def check_round_over(self):
        """Check if the current round is over (any player has no cards left)"""
        # First check if any player has no cards left
        for player in self.players:
            if len(player.hand) == 0:
                # Count how many jacks were in the last play
                jack_count = 0
                if self.table_cards:
                    # Look at the last cards played (they must be from the player who went out)
                    last_rank = self.table_cards[-1].rank
                    if last_rank == 11:  # It was a Jack
                        # Count consecutive Jacks from the end
                        for card in reversed(self.table_cards):
                            if card.rank == 11:
                                jack_count += 1
                            else:
                                break
                                
                # Calculate and apply the Jack bonus (negative points)
                jack_bonus = -20 * jack_count * self.point_multiplier if jack_count > 0 else 0
                
                # Calculate opponent points
                opponent = self.players[1] if player == self.players[0] else self.players[0]
                opponent_points = opponent.calculate_hand_points() * self.point_multiplier
                
                # Add points to opponent and apply Jack bonus to winner if applicable
                opponent.points += opponent_points
                if jack_bonus < 0:
                    player.points += jack_bonus  # Add negative points (subtract)
                
                # Check if overall game is over
                if opponent.points > 125:
                    self.is_running = False
                    # The player who went out (no cards left) is the winner of this round
                    # But the overall game is won by the player with FEWER points
                    winner = "Player" if self.players[1].points > self.players[0].points else "Computer"
                    self.round_end_message = f"Game Over! {winner} wins! Final score: Player {self.players[0].points}, Computer {self.players[1].points}"
                    display_message(self.round_end_message)
                    return True
                
                winner = "Player" if player == self.players[0] else "Computer"
                loser = "Player" if player != self.players[0] else "Computer"
                jack_text = ""
                
                # If there was a Jack bonus, include it in the message
                jack_count = 0
                if self.table_cards and self.table_cards[-1].rank == 11:
                    # Count consecutive Jacks from the end
                    for card in reversed(self.table_cards):
                        if card.rank == 11:
                            jack_count += 1
                        else:
                            break
                    if jack_count > 0:
                        jack_bonus = -20 * jack_count * self.point_multiplier
                        jack_text = f" {winner} finished with {jack_count} Jack{'s' if jack_count > 1 else ''} (-{abs(jack_bonus)} points)!"
                
                self.round_end_message = f"Round {self.round_number} over! {winner} wins!{jack_text} {loser} gets {opponent_points} points (×{self.point_multiplier} multiplier). Total score: Player {self.players[0].points}, Computer {self.players[1].points}"
                display_message(self.round_end_message)
                return True
                
        # Check if both players are deadlocked (neither can play and deck is empty)
        if not self.deck.cards:
            human = self.players[0]
            computer = self.players[1]
            
            if not self.has_valid_play(human) and not self.has_valid_play(computer):
                # Round is deadlocked - calculate points for both players
                human_points = human.calculate_hand_points() * self.point_multiplier
                computer_points = computer.calculate_hand_points() * self.point_multiplier
                
                human.points += computer_points
                computer.points += human_points
                
                # Check if overall game is over
                if human.points > 125 or computer.points > 125:
                    self.is_running = False
                    if human.points > 125 and computer.points > 125:
                        winner = "Computer" if computer.points < human.points else "Player"
                    else:
                        winner = "Computer" if human.points > 125 else "Player"
                        
                    self.round_end_message = f"Game Over! {winner} wins! Final score: Player {human.points}, Computer {computer.points}"
                    display_message(self.round_end_message)
                    return True
                
                self.round_end_message = f"Round {self.round_number} deadlocked! Both players get points: Player +{computer_points}, Computer +{human_points}. Total score: Player {human.points}, Computer {computer.points}"
                display_message(self.round_end_message)
                return True
                
        return False

    def check_game_over(self):
        """Check if the overall game is over (any player exceeds 125 points)"""
        for player in self.players:
            if player.points > 125:
                self.is_running = False
                winner = "Player" if player != self.players[0] else "Computer"
                self.round_end_message = f"Game Over! {winner} wins with fewer points! Final score: Player {self.players[0].points}, Computer {self.players[1].points}"
                display_message(self.round_end_message)
                return True
        return False

    def end_game(self):
        """End the game gracefully"""
        self.is_running = False
        display_message("\nGame Over!")

    def can_play_card(self, card):
        """
        Check if a card can be played according to the rules:
        1. If the table is empty, any card can be played
        2. If card is a Jack, it can be played on anything (any suit, any rank)
        3. If a suit is enforced by a Jack, only that suit or another Jack can be played
        4. Card can be played if it has the same suit as the top card
        5. Card can be played if it has the same rank as the top card
        6. Special case for 6s: must be followed by another 6, same suit, or any Jack
        """
        # If there are no cards on the table, any card can be played
        if not self.table_cards:
            return True
            
        # Get the top card on the table
        top_card = self.table_cards[-1]
        
        # Special case for 6s: only the same player can play on it during their turn
        if self.pending_effects['requires_six']:
            current_player = self.players[self.current_player_index]
            if current_player != self.pending_effects['six_player']:
                # Different player cannot interfere with opponent's 6 at all
                return False
            
            # Same player: Must play another 6, same suit as the most recent 6, or any Jack
            six_suit = self.pending_effects['six_suit']
            return card.rank == 6 or card.suit == six_suit or card.rank == 11
            
        # Any Jack (rank 11) can be played on any card or suit (except when different player tries to cover opponent's 6)
        if card.rank == 11:
            return True  # All Jacks are wild - can be played anytime, on any suit
            
        # If a suit is being enforced by a Jack
        if self.pending_effects['suit_enforced'] and self.pending_effects['chosen_suit']:
            # Can only play the enforced suit or another Jack
            return card.suit == self.pending_effects['chosen_suit'] or card.rank == 11
            
        # Card can be played if same suit or same rank
        return card.suit == top_card.suit or card.rank == top_card.rank

    def has_valid_play(self, player):
        """Check if the player has any valid card to play"""
        for card in player.hand:
            if self.can_play_card(card):
                return True
        return False

    def reshuffle_table_cards(self):
        """Reshuffle cards from the table to create a new deck when the current one is empty"""
        if not self.table_cards or len(self.table_cards) <= 1:
            return False  # Not enough cards on the table to reshuffle
            
        display_message("Reshuffling cards from the table to create a new deck")
        
        # Keep the last played card on the table
        top_card = self.table_cards.pop()
        
        # Move all other cards from the table to the deck
        self.deck.cards = self.table_cards.copy()
        self.table_cards = [top_card]  # Reset the table cards to only the top card
        
        # Shuffle the deck
        self.deck.shuffle()
        
        # Increase the point multiplier for the next round
        self.point_multiplier += 1
        
        display_message(f"Cards reshuffled! Point multiplier increased to ×{self.point_multiplier}")
        return True

    def draw_until_playable(self, player):
        """Draw one card when player has no playable cards. If still no playable card, turn is skipped."""
        # If deck is empty, try to reshuffle cards from the table
        if not self.deck.cards:
            if self.reshuffle_table_cards():
                display_message(f"Deck was empty! Cards reshuffled for {player.name}")
            else:
                display_message(f"Deck is empty and cannot reshuffle! {player.name} skips their turn")
                return False
        
        # Draw exactly one card
        card = self.deck.draw_card()
        
        if card:
            player.add_card(card)
            display_message(f"{player.name} has no playable cards - drew: {card.get_card_info()}")
            
            # Check if the card is playable
            if self.can_play_card(card):
                display_message(f"{player.name} can now play the card they drew")
                return True
            else:
                display_message(f"{player.name} still has no playable cards - turn skipped")
                return False
        else:
            # Couldn't draw a card even after potential reshuffle
            display_message(f"{player.name} couldn't draw a card - turn skipped")
            return False

    def draw_until_six_covered(self, player):
        """Draw multiple cards until player finds one that can cover a 6, or deck is empty."""
        cards_drawn = 0
        max_draws = 10  # Safety limit to prevent infinite loops
        
        while cards_drawn < max_draws:
            # If deck is empty, try to reshuffle cards from the table
            if not self.deck.cards:
                if self.reshuffle_table_cards():
                    display_message(f"Deck was empty! Cards reshuffled for {player.name}")
                else:
                    display_message(f"Deck is empty and cannot reshuffle! {player.name} cannot cover the 6")
                    return False
            
            # Draw a card
            card = self.deck.draw_card()
            cards_drawn += 1
            
            if card:
                player.add_card(card)
                display_message(f"{player.name} drew: {card.get_card_info()} (trying to cover 6)")
                
                # Check if this card can cover the 6
                if self.can_play_card(card):
                    display_message(f"{player.name} found a card to cover the 6 after drawing {cards_drawn} cards")
                    return True
            else:
                # Couldn't draw a card
                display_message(f"{player.name} couldn't draw a card - cannot cover the 6")
                return False
        
        display_message(f"{player.name} drew {max_draws} cards but still cannot cover the 6")
        return False
    
    def choose_strategic_suit(self, player):
        """Choose a strategic suit when playing a Jack:
        1. Choose the suit with the most cards in the player's hand
        2. If multiple suits have the same count, prefer hearts, diamonds, clubs, spades in that order
        """
        # Count cards by suit
        suit_counts = {'H': 0, 'D': 0, 'C': 0, 'S': 0}
        for card in player.hand:
            if card.suit in suit_counts:
                suit_counts[card.suit] += 1
        
        # Find the suit with the most cards
        max_count = 0
        best_suit = 'H'  # Default to hearts if no cards
        
        # Preferred suit order
        suit_order = ['H', 'D', 'C', 'S']
        
        # First check if we have a clear winner
        for suit, count in suit_counts.items():
            if count > max_count:
                max_count = count
                best_suit = suit
                
        # If there's a tie, prefer hearts > diamonds > clubs > spades
        tied_suits = [s for s, c in suit_counts.items() if c == max_count]
        if len(tied_suits) > 1:
            for suit in suit_order:
                if suit in tied_suits:
                    best_suit = suit
                    break
                    
        return best_suit
    
    def set_player_effect_callback(self, callback):
        """Set a callback function to notify the GUI when players are affected by card effects"""
        self.on_player_effect_callback = callback