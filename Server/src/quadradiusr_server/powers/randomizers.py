import random
import uuid
from typing import List, Optional

from quadradiusr_server.game_state import GameState, Power
from quadradiusr_server.powers import PowerRandomizer, PowerDefinition


class DefaultPowerRandomizer(PowerRandomizer):
    _power_chance = 0.3

    def after_move(
            self, game_state: GameState,
            power_definitions: List[PowerDefinition]) -> None:
        if random.uniform(0, 1) > self._power_chance:
            return

        tile_id = self._random_tile(game_state)
        if tile_id is None:
            return
        power = Power(
            id=str(uuid.uuid4()),
            power_definition_id=self._random_power_definition(power_definitions),
            tile_id=tile_id,
        )
        game_state.board.powers[power.id] = power

    def _random_tile(self, game_state: GameState) -> Optional[str]:
        tile_ids = list(game_state.board.get_empty_tiles().keys())
        if len(tile_ids) == 0:
            return
        return random.choice(tile_ids)

    def _random_power_definition(self, power_definitions: List[PowerDefinition]) -> str:
        pd = random.choice(power_definitions)
        return pd.get_id()
