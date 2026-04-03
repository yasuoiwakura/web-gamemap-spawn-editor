from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import GameCreate, Game
from ..services.dynamodb import db_service
from ..utils import cors_response

router = APIRouter(prefix="/games", tags=["games"])


@router.get("")
def get_games():
    return cors_response(db_service.get_all_games())


@router.get("/{game_id}")
def get_game(game_id: str):
    game = db_service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return cors_response(game)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_game(game: GameCreate):
    return cors_response(
        db_service.create_game(name=game.name, icon_url=game.iconUrl),
        status_code=status.HTTP_201_CREATED
    )


@router.put("/{game_id}")
def update_game(game_id: str, game: GameCreate):
    existing = db_service.get_game(game_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Game not found")
    return cors_response(db_service.update_game(game_id, name=game.name, icon_url=game.iconUrl))


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: str):
    existing = db_service.get_game(game_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Game not found")
    db_service.delete_game(game_id)
    return cors_response(None, status_code=status.HTTP_204_NO_CONTENT)
