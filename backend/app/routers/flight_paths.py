from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Any
from ..models import FlightPathCreate, FlightPath
from ..services.dynamodb import db_service

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def cors_response(content: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse(content=content, status_code=status_code, headers=CORS_HEADERS)


router = APIRouter(prefix="/maps/{map_id}/flight-paths", tags=["flight-paths"])


@router.get("")
def get_flight_paths(map_id: str):
    return cors_response(db_service.get_flight_paths_by_map(map_id))


@router.post("")
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


@router.delete("/{flight_path_id}")
def delete_flight_path(map_id: str, flight_path_id: str):
    existing = db_service.get_flight_path(flight_path_id)
    if not existing or existing.get('mapId') != map_id:
        raise HTTPException(status_code=404, detail="Flight path not found")
    db_service.delete_flight_path(flight_path_id)
    return cors_response(None, status_code=status.HTTP_204_NO_CONTENT)
