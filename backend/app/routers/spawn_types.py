from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Any
from ..models import SpawnTypeCreate, SpawnType
from ..services.dynamodb import db_service

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def cors_response(content: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse(content=content, status_code=status_code, headers=CORS_HEADERS)


router = APIRouter(prefix="/games/{game_id}/spawn-types", tags=["spawn-types"])


@router.get("")
def get_spawn_types(game_id: str):
    return cors_response(db_service.get_spawn_types_by_game(game_id))


@router.post("")
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
