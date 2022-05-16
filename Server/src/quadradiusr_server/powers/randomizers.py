import random
import uuid
from typing import List, Optional

from quadradiusr_server.game_state import GameState, Power, NextPowerSpawnInfo
from quadradiusr_server.powers import PowerRandomizer, PowerDefinition


class DefaultPowerRandomizer(PowerRandomizer):
    def initial_spawn_info(self) -> NextPowerSpawnInfo:
        return self._random_spawn_info()

    def after_move(
            self, game_state: GameState,
            power_definitions: List[PowerDefinition]) -> None:
        spawn_info: NextPowerSpawnInfo = game_state.next_power_spawn
        spawn_info.rounds -= 1
        if spawn_info.rounds > 0:
            return

        for i in range(spawn_info.count):
            tile_id = self._random_tile(game_state)
            if tile_id is None:
                return
            power = Power(
                id=str(uuid.uuid4()),
                power_definition_id=self._random_power_definition(power_definitions),
                tile_id=tile_id,
            )
            game_state.board.powers[power.id] = power

        game_state.next_power_spawn = self._random_spawn_info()

    def _random_spawn_info(self) -> NextPowerSpawnInfo:
        return NextPowerSpawnInfo(
            rounds=random.choices(
                [1, 2, 3, 4, 5, 6, 7],
                [1, 2, 3, 4, 5, 5, 5])[0],
            count=random.randint(1, 3),
        )

    def _random_tile(self, game_state: GameState) -> Optional[str]:
        tile_ids = list(game_state.board.get_empty_tiles().keys())
        if len(tile_ids) == 0:
            return
        return random.choice(tile_ids)

    def _random_power_definition(self, power_definitions: List[PowerDefinition]) -> str:
        pd = random.choice(power_definitions)
        return pd.get_id()
