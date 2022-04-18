from abc import ABC, abstractmethod
from typing import Optional, List

from quadradiusr_server.game import GameState
from quadradiusr_server.utils import import_submodules


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


class PowerDefinitionList:
    def __init__(self) -> None:
        self._definitions = dict()

    def declare(self, clazz):
        if not issubclass(clazz, PowerDefinition):
            raise ValueError(f'Class {clazz} is not a subclass of {PowerDefinition}')

        power_def = clazz()
        self._definitions[power_def.get_id()] = power_def

        return clazz

    def get_by_id(self, power_definition_id: str) -> Optional[PowerDefinition]:
        if power_definition_id in self._definitions:
            return self._definitions[power_definition_id]
        return None

    def get_all(self) -> List[PowerDefinition]:
        return list(self._definitions.values())


power_definitions = PowerDefinitionList()

import_submodules(__name__)
