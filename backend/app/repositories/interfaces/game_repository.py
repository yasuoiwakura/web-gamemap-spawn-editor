from typing import Optional, List
from abc import ABC, abstractmethod

from app.models import Game, GameCreate


class GameRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Game]:
        pass

    @abstractmethod
    def get_by_id(self, game_id: str) -> Optional[Game]:
        pass

    @abstractmethod
    def create(self, game: GameCreate) -> Game:
        pass

    @abstractmethod
    def update(self, game_id: str, game: GameCreate) -> Optional[Game]:
        pass

    @abstractmethod
    def delete(self, game_id: str) -> bool:
        pass
