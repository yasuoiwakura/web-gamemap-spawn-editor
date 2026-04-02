from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import FlightPathCreate, FlightPath
from ..repositories import get_repository_factory

router = APIRouter(prefix="/maps/{map_id}/flight-paths", tags=["flight-paths"])


@router.get("", response_model=List[FlightPath])
def get_flight_paths(map_id: str):
    repo = get_repository_factory().get_flight_path_repository()
    return repo.get_by_map(map_id)


@router.post("", response_model=FlightPath, status_code=status.HTTP_201_CREATED)
def create_flight_path(map_id: str, flight_path: FlightPathCreate):
    repo = get_repository_factory().get_flight_path_repository()
    return repo.create(map_id, flight_path)


@router.delete("/{flight_path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flight_path(map_id: str, flight_path_id: str):
    repo = get_repository_factory().get_flight_path_repository()
    existing = repo.get_by_id(flight_path_id)
    if not existing or existing.mapId != map_id:
        raise HTTPException(status_code=404, detail="Flight path not found")
    repo.delete(flight_path_id)
    return None