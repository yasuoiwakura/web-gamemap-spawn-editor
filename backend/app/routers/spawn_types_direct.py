from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from ..services.dynamodb import db_service

router = APIRouter(prefix="/spawn-types", tags=["spawn-types"])


class SpawnTypeUpdate(BaseModel):
    name: str = None
    color: str = None
    iconType: str = None
    rotationEnabled: bool = None


@router.get("/{spawn_type_id}")
def get_spawn_type(spawn_type_id: str):
    spawn_type = db_service.get_spawn_type(spawn_type_id)
    if not spawn_type:
        raise HTTPException(status_code=404, detail="Spawn type not found")
    return spawn_type


@router.put("/{spawn_type_id}")
def update_spawn_type(spawn_type_id: str, spawn_type_update: SpawnTypeUpdate):
    existing = db_service.get_spawn_type(spawn_type_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Spawn type not found")
    return db_service.update_spawn_type(
        spawn_type_id,
        name=spawn_type_update.name,
        color=spawn_type_update.color,
        icon_type=spawn_type_update.iconType,
        rotation_enabled=spawn_type_update.rotationEnabled
    )


@router.delete("/{spawn_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spawn_type(spawn_type_id: str):
    existing = db_service.get_spawn_type(spawn_type_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Spawn type not found")
    db_service.delete_spawn_type(spawn_type_id)
    return None