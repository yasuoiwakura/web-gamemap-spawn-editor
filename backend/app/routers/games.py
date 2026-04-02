from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import GameCreate, Game
from ..services.dynamodb import db_service

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=List[Game])
def get_games():
    return db_service.get_all_games()


@router.get("/{game_id}", response_model=Game)
def get_game(game_id: str):
    game = db_service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.post("", response_model=Game, status_code=status.HTTP_201_CREATED)
def create_game(game: GameCreate):
    return db_service.create_game(name=game.name, icon_url=game.iconUrl)


@router.put("/{game_id}", response_model=Game)
def update_game(game_id: str, game: GameCreate):
    existing = db_service.get_game(game_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_service.update_game(game_id, name=game.name, icon_url=game.iconUrl)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: str):
    existing = db_service.get_game(game_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Game not found")
    db_service.delete_game(game_id)
    return None