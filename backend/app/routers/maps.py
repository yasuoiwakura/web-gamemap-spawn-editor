from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import MapCreate, Map
from ..services.dynamodb import db_service

router = APIRouter(prefix="/games/{game_id}/maps", tags=["maps"])


@router.get("", response_model=List[Map])
def get_maps(game_id: str):
    return db_service.get_maps_by_game(game_id)


@router.post("", response_model=Map, status_code=status.HTTP_201_CREATED)
def create_map(game_id: str, map: MapCreate):
    return db_service.create_map(
        game_id=game_id,
        name=map.name,
        image_url=map.imageUrl,
        width_px=map.widthPx,
        height_px=map.heightPx,
        real_size_meters=map.realSizeMeters
    )