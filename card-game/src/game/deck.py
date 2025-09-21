import random
from .card import Card

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in range(1, 14) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']]
    
    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None