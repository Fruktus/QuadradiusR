from unittest import TestCase

from harness import GameHarness
from quadradiusr_server.game import GameState


class TestGame(GameHarness, TestCase):
    def test_initial(self):
        initial = GameState.initial('player_a', 'player_b')

        for x in range(10):
            for y in range(2):
                piece = initial.board.get_piece_at(x, y)
                self.assertEqual('player_a', piece.owner_id)

        for x in range(10):
            for y in range(6, 8):
                piece = initial.board.get_piece_at(x, y)
                self.assertEqual('player_b', piece.owner_id)
