import os
from typing import Optional

from app.repositories.interfaces import (
    GameRepository,
    MapRepository,
    SpawnTypeRepository,
    POIRepository,
    FlightPathRepository,
)
from app.repositories.implementations import (
    DynamoDBGameRepository,
    DynamoDBMapRepository,
    DynamoDBSpawnTypeRepository,
    DynamoDBPOIRepository,
    DynamoDBFlightPathRepository,
)
from app.repositories.dynamodb_client import DynamoDBClient


class RepositoryFactory:
    def __init__(self, db_type: str = "dynamodb"):
        self._db_type = db_type
        self._client: Optional[DynamoDBClient] = None
        self._game_repo: Optional[GameRepository] = None
        self._map_repo: Optional[MapRepository] = None
        self._spawn_type_repo: Optional[SpawnTypeRepository] = None
        self._poi_repo: Optional[POIRepository] = None
        self._flight_path_repo: Optional[FlightPathRepository] = None

    def _get_dynamodb_client(self) -> DynamoDBClient:
        if self._client is None:
            table_suffix = os.environ.get("TABLE_SUFFIX", "")
            self._client = DynamoDBClient(table_suffix=table_suffix)
        return self._client

    def get_game_repository(self) -> GameRepository:
        if self._db_type == "dynamodb":
            if self._game_repo is None:
                self._game_repo = DynamoDBGameRepository(self._get_dynamodb_client())
            return self._game_repo
        raise ValueError(f"Unsupported database type: {self._db_type}")

    def get_map_repository(self) -> MapRepository:
        if self._db_type == "dynamodb":
            if self._map_repo is None:
                self._map_repo = DynamoDBMapRepository(self._get_dynamodb_client())
            return self._map_repo
        raise ValueError(f"Unsupported database type: {self._db_type}")

    def get_spawn_type_repository(self) -> SpawnTypeRepository:
        if self._db_type == "dynamodb":
            if self._spawn_type_repo is None:
                self._spawn_type_repo = DynamoDBSpawnTypeRepository(self._get_dynamodb_client())
            return self._spawn_type_repo
        raise ValueError(f"Unsupported database type: {self._db_type}")

    def get_poi_repository(self) -> POIRepository:
        if self._db_type == "dynamodb":
            if self._poi_repo is None:
                self._poi_repo = DynamoDBPOIRepository(self._get_dynamodb_client())
            return self._poi_repo
        raise ValueError(f"Unsupported database type: {self._db_type}")

    def get_flight_path_repository(self) -> FlightPathRepository:
        if self._db_type == "dynamodb":
            if self._flight_path_repo is None:
                self._flight_path_repo = DynamoDBFlightPathRepository(self._get_dynamodb_client())
            return self._flight_path_repo
        raise ValueError(f"Unsupported database type: {self._db_type}")


_repo_factory: Optional[RepositoryFactory] = None


def get_repository_factory() -> RepositoryFactory:
    global _repo_factory
    if _repo_factory is None:
        db_type = os.environ.get("DB_TYPE", "dynamodb")
        _repo_factory = RepositoryFactory(db_type=db_type)
    return _repo_factory
