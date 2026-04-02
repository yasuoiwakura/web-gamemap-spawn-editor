from typing import Optional, List
from abc import ABC, abstractmethod

from app.models import POI, POICreate


class POIRepository(ABC):
    @abstractmethod
    def get_by_map(self, map_id: str) -> List[POI]:
        pass

    @abstractmethod
    def get_by_id(self, poi_id: str) -> Optional[POI]:
        pass

    @abstractmethod
    def create(self, map_id: str, poi: POICreate) -> POI:
        pass

    @abstractmethod
    def update(self, poi_id: str, poi_data: dict) -> Optional[POI]:
        pass

    @abstractmethod
    def delete(self, poi_id: str) -> bool:
        pass
