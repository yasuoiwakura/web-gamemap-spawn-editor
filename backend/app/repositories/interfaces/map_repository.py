from typing import Optional, List
from abc import ABC, abstractmethod

from app.models import Map, MapCreate


class MapRepository(ABC):
    @abstractmethod
    def get_by_game(self, game_id: str) -> List[Map]:
        pass

    @abstractmethod
    def get_by_id(self, map_id: str) -> Optional[Map]:
        pass

    @abstractmethod
    def create(self, game_id: str, map: MapCreate) -> Map:
        pass

    @abstractmethod
    def update(self, map_id: str, map_data: dict) -> Optional[Map]:
        pass

    @abstractmethod
    def delete(self, map_id: str) -> bool:
        pass
