from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import SpawnTypeCreate, SpawnType
from ..services.dynamodb import db_service

router = APIRouter(prefix="/games/{game_id}/spawn-types", tags=["spawn-types"])


@router.get("", response_model=List[SpawnType])
def get_spawn_types(game_id: str):
    return db_service.get_spawn_types_by_game(game_id)


@router.post("", response_model=SpawnType, status_code=status.HTTP_201_CREATED)
def create_spawn_type(game_id: str, spawn_type: SpawnTypeCreate):
    return db_service.create_spawn_type(
        game_id=game_id,
        name=spawn_type.name,
        color=spawn_type.color,
        icon_type=spawn_type.iconType,
        rotation_enabled=spawn_type.rotationEnabled
    )