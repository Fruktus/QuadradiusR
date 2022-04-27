from abc import ABC, abstractmethod
from typing import List

from quadradiusr_server.game_state import GameState


class PowerDefinition(ABC):
    @abstractmethod
    def get_id(self) -> str:
        ...

    @abstractmethod
    def get_name(self) -> str:
        ...

    @abstractmethod
    def get_description(self) -> str:
        ...

    @abstractmethod
    def apply(self, game_state: GameState, power_id: str) -> None:
        ...


class PowerRandomizer(ABC):
    @abstractmethod
    def after_move(
            self, game_state: GameState,
            power_definitions: List[PowerDefinition]) -> None:
        ...
