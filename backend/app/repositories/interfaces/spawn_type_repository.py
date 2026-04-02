from typing import Optional, List
from abc import ABC, abstractmethod

from app.models import SpawnType, SpawnTypeCreate


class SpawnTypeRepository(ABC):
    @abstractmethod
    def get_by_game(self, game_id: str) -> List[SpawnType]:
        pass

    @abstractmethod
    def get_by_id(self, spawn_type_id: str) -> Optional[SpawnType]:
        pass

    @abstractmethod
    def create(self, game_id: str, spawn_type: SpawnTypeCreate) -> SpawnType:
        pass

    @abstractmethod
    def update(self, spawn_type_id: str, spawn_type_data: dict) -> Optional[SpawnType]:
        pass

    @abstractmethod
    def delete(self, spawn_type_id: str) -> bool:
        pass
