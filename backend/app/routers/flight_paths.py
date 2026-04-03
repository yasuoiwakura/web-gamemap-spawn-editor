from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import FlightPathCreate, FlightPath
from ..services.dynamodb import db_service
from ..utils import cors_response

router = APIRouter(prefix="/maps/{map_id}/flight-paths", tags=["flight-paths"])


@router.get("")
def get_flight_paths(map_id: str):
    return cors_response(db_service.get_flight_paths_by_map(map_id))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_flight_path(map_id: str, flight_path: FlightPathCreate):
    return cors_response(
        db_service.create_flight_path(
            map_id=map_id,
            start_x=flight_path.startX,
            start_y=flight_path.startY,
            end_x=flight_path.endX,
            end_y=flight_path.endY
        ),
        status_code=status.HTTP_201_CREATED
    )


@router.delete("/{flight_path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flight_path(map_id: str, flight_path_id: str):
    existing = db_service.get_flight_path(flight_path_id)
    if not existing or existing.get('mapId') != map_id:
        raise HTTPException(status_code=404, detail="Flight path not found")
    db_service.delete_flight_path(flight_path_id)
    return cors_response(None, status_code=status.HTTP_204_NO_CONTENT)
