from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import GameCreate, Game
from ..repositories import get_repository_factory

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=List[Game])
def get_games():
    repo = get_repository_factory().get_game_repository()
    return repo.get_all()


@router.get("/{game_id}", response_model=Game)
def get_game(game_id: str):
    repo = get_repository_factory().get_game_repository()
    game = repo.get_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.post("", response_model=Game, status_code=status.HTTP_201_CREATED)
def create_game(game: GameCreate):
    repo = get_repository_factory().get_game_repository()
    return repo.create(game)


@router.put("/{game_id}", response_model=Game)
def update_game(game_id: str, game: GameCreate):
    repo = get_repository_factory().get_game_repository()
    existing = repo.get_by_id(game_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Game not found")
    return repo.update(game_id, game)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: str):
    repo = get_repository_factory().get_game_repository()
    existing = repo.get_by_id(game_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Game not found")
    repo.delete(game_id)
    return None