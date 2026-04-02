from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import MapCreate, Map
from ..repositories import get_repository_factory

router = APIRouter(prefix="/games/{game_id}/maps", tags=["maps"])


@router.get("", response_model=List[Map])
def get_maps(game_id: str):
    repo = get_repository_factory().get_map_repository()
    return repo.get_by_game(game_id)


@router.post("", response_model=Map, status_code=status.HTTP_201_CREATED)
def create_map(game_id: str, map: MapCreate):
    repo = get_repository_factory().get_map_repository()
    return repo.create(game_id, map)