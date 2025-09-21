# filepath: c:\Python\BridgeGame\card-game\tests\test_game.py
import unittest
from src.game.game import Game
from src.game.player import Player

class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()
        self.game.players = [Player("Alice"), Player("Bob")]
        self.game.start_game()

    def test_start_game(self):
        self.assertTrue(self.game.is_running)

    def test_play_turn(self):
        initial_player_count = len(self.game.players)
        self.game.play_turn(self.game.players[0])
        self.assertEqual(len(self.game.players), initial_player_count)

    def test_end_game(self):
        self.game.end_game()
        self.assertFalse(self.game.is_running)

if __name__ == '__main__':
    unittest.main()