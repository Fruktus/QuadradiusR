from unittest import TestCase

from harness import GameHarness
from quadradiusr_server.game_state import GameState, Tile, Piece, GameBoard, Power


class TestGameState(GameHarness, TestCase):
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


class TestGameBoard(GameHarness, TestCase):
    def test_get_empty_tiles(self):
        board = GameBoard(
            tiles={
                # tile with piece on it
                '0': Tile(
                    id='0',
                    position=(0, 0),
                ),
                # tile clear
                '1': Tile(
                    id='1',
                    position=(0, 1),
                ),
                # tile with power on it
                '2': Tile(
                    id='2',
                    position=(0, 2),
                ),
                # tile clear
                '3': Tile(
                    id='3',
                    position=(0, 3),
                ),
            },
            pieces={
                '0': Piece(
                    id='0',
                    tile_id='0',
                    owner_id='a',
                ),
            },
            powers={
                '0': Power(
                    id='0',
                    power_definition_id='raise_tile',
                    tile_id='2',
                ),
            },
        )
        self.assertSetEqual(
            {'1', '3'},
            set(board.get_empty_tiles().keys()))
