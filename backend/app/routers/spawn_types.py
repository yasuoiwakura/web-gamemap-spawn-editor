from fastapi import APIRouter, status
from typing import List
from ..models import SpawnTypeCreate, SpawnType
from ..services.dynamodb import db_service
from ..utils import cors_response

router = APIRouter(prefix="/games/{game_id}/spawn-types", tags=["spawn-types"])


@router.get("")
def get_spawn_types(game_id: str):
    return cors_response(db_service.get_spawn_types_by_game(game_id))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_spawn_type(game_id: str, spawn_type: SpawnTypeCreate):
    return cors_response(
        db_service.create_spawn_type(
            game_id=game_id,
            name=spawn_type.name,
            color=spawn_type.color,
            icon_type=spawn_type.iconType,
            rotation_enabled=spawn_type.rotationEnabled
        ),
        status_code=status.HTTP_201_CREATED
    )
