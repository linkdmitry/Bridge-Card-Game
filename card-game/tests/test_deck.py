# filepath: c:\Python\BridgeGame\card-game\tests\test_deck.py
import unittest
from src.game.deck import Deck
from src.game.card import Card

class TestDeck(unittest.TestCase):

    def setUp(self):
        self.deck = Deck()

    def test_deck_initialization(self):
        self.assertEqual(len(self.deck.cards), 52)

    def test_shuffle(self):
        original_order = self.deck.cards[:]
        self.deck.shuffle()
        self.assertNotEqual(original_order, self.deck.cards)

    def test_draw_card(self):
        card = self.deck.draw_card()
        self.assertIsInstance(card, Card)
        self.assertEqual(len(self.deck.cards), 51)

if __name__ == '__main__':
    unittest.main()