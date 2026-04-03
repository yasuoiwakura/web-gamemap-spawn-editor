from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import MapCreate, Map
from ..services.dynamodb import db_service
from ..utils import cors_response

router = APIRouter(prefix="/games/{game_id}/maps", tags=["maps"])


@router.get("")
def get_maps(game_id: str):
    return cors_response(db_service.get_maps_by_game(game_id))


@router.post("", status_code=status.HTTP_201_CREATED)
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
