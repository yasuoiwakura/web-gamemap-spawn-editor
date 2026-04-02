from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Any
from ..models import GameCreate, Game
from ..services.dynamodb import db_service

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def cors_response(content: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse(content=content, status_code=status_code, headers=CORS_HEADERS)


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


@router.post("")
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


@router.delete("/{game_id}")
def delete_game(game_id: str):
    existing = db_service.get_game(game_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Game not found")
    db_service.delete_game(game_id)
    return cors_response(None, status_code=status.HTTP_204_NO_CONTENT)
