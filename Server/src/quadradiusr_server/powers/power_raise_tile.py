from quadradiusr_server.game import GameState
from quadradiusr_server.powers import PowerDefinition, power_definitions


@power_definitions.declare
class RaiseTilePowerDefinition(PowerDefinition):
    def get_id(self) -> str:
        return 'raise_tile'

    def get_name(self) -> str:
        return 'Raise Tile'

    def get_description(self) -> str:
        return 'Raises the tile'

    def apply(self, game_state: GameState, power_id: str) -> None:
        power = game_state.board.powers[power_id]
        if not power.piece_id:
            raise ValueError(f'No piece ID for power {power_id}')

        piece = game_state.board.pieces[power.piece_id]
        tile = game_state.board.tiles[piece.tile_id]
        tile.elevation += 1
