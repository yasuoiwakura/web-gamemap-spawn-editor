from typing import Optional, List
from abc import ABC, abstractmethod

from app.models import FlightPath, FlightPathCreate


class FlightPathRepository(ABC):
    @abstractmethod
    def get_by_map(self, map_id: str) -> List[FlightPath]:
        pass

    @abstractmethod
    def get_by_id(self, flight_path_id: str) -> Optional[FlightPath]:
        pass

    @abstractmethod
    def create(self, map_id: str, flight_path: FlightPathCreate) -> FlightPath:
        pass

    @abstractmethod
    def delete(self, flight_path_id: str) -> bool:
        pass
