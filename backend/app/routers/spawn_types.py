from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import SpawnTypeCreate, SpawnType
from ..repositories import get_repository_factory

router = APIRouter(prefix="/games/{game_id}/spawn-types", tags=["spawn-types"])


@router.get("", response_model=List[SpawnType])
def get_spawn_types(game_id: str):
    repo = get_repository_factory().get_spawn_type_repository()
    return repo.get_by_game(game_id)


@router.post("", response_model=SpawnType, status_code=status.HTTP_201_CREATED)
def create_spawn_type(game_id: str, spawn_type: SpawnTypeCreate):
    repo = get_repository_factory().get_spawn_type_repository()
    return repo.create(game_id, spawn_type)