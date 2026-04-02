from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import FlightPathCreate, FlightPath
from ..services.dynamodb import db_service

router = APIRouter(prefix="/maps/{map_id}/flight-paths", tags=["flight-paths"])


@router.get("", response_model=List[FlightPath])
def get_flight_paths(map_id: str):
    return db_service.get_flight_paths_by_map(map_id)


@router.post("", response_model=FlightPath, status_code=status.HTTP_201_CREATED)
def create_flight_path(map_id: str, flight_path: FlightPathCreate):
    return db_service.create_flight_path(
        map_id=map_id,
        start_x=flight_path.startX,
        start_y=flight_path.startY,
        end_x=flight_path.endX,
        end_y=flight_path.endY
    )


@router.delete("/{flight_path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flight_path(map_id: str, flight_path_id: str):
    existing = db_service.get_flight_path(flight_path_id)
    if not existing or existing.get('mapId') != map_id:
        raise HTTPException(status_code=404, detail="Flight path not found")
    db_service.delete_flight_path(flight_path_id)
    return None