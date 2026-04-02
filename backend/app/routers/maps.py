from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Any
from ..models import MapCreate, Map
from ..services.dynamodb import db_service

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def cors_response(content: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse(content=content, status_code=status_code, headers=CORS_HEADERS)


router = APIRouter(prefix="/games/{game_id}/maps", tags=["maps"])


@router.get("")
def get_maps(game_id: str):
    return cors_response(db_service.get_maps_by_game(game_id))


@router.post("")
def create_map(game_id: str, map: MapCreate):
    return cors_response(
        db_service.create_map(
            game_id=game_id,
            name=map.name,
            image_url=map.imageUrl,
            width_px=map.widthPx,
            height_px=map.heightPx,
            real_size_meters=map.realSizeMeters
        ),
        status_code=status.HTTP_201_CREATED
    )
