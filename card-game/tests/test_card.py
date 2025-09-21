# filepath: c:\Python\BridgeGame\card-game\tests\test_card.py
import unittest
from src.game.card import Card

class TestCard(unittest.TestCase):

    def setUp(self):
        self.card = Card(rank='Ace', suit='Hearts')

    def test_card_properties(self):
        self.assertEqual(self.card.rank, 'Ace')
        self.assertEqual(self.card.suit, 'Hearts')

    def test_get_card_info(self):
        self.assertEqual(self.card.get_card_info(), 'Ace of Hearts')

if __name__ == '__main__':
    unittest.main()