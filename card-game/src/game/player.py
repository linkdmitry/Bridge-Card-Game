class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.points = 0  # Track player's points across rounds

    def add_card(self, card):
        self.hand.append(card)

    def show_hand(self):
        return [card.get_card_info() for card in self.hand]

    def count_playable_cards(self, game):
        """Count how many cards can be played according to game rules"""
        playable_count = 0
        for card in self.hand:
            if game.can_play_card(card):
                playable_count += 1
        return playable_count

    def get_playable_cards(self, game):
        """Return a list of playable cards"""
        return [card for card in self.hand if game.can_play_card(card)]

    def has_card_of_suit(self, suit):
        """Check if player has a card of the specified suit"""
        return any(card.suit == suit for card in self.hand)

    def has_card_of_rank(self, rank):
        """Check if player has a card of the specified rank"""
        return any(card.rank == rank for card in self.hand)
        
    def calculate_hand_points(self):
        """Calculate points from cards in hand based on the game's scoring system"""
        points = 0
        for card in self.hand:
            if 2 <= card.rank <= 9:
                # Cards 2-9 are worth 0 points
                continue
            elif card.rank == 10:
                # Card 10 is worth 10 points
                points += 10
            elif card.rank == 11:
                # Jack is worth 20 points
                points += 20
            elif card.rank in (12, 13):
                # Queen and King are worth 10 points
                points += 10
            elif card.rank == 1:
                # Ace is worth 15 points
                points += 15
        return points