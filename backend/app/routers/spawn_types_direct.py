from fastapi import APIRouter, HTTPException, status
from typing import Optional
from pydantic import BaseModel
from ..models import SpawnType
from ..repositories import get_repository_factory

router = APIRouter(prefix="/spawn-types", tags=["spawn-types"])


class SpawnTypeUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    iconType: Optional[str] = None
    rotationEnabled: Optional[bool] = None


@router.get("/{spawn_type_id}", response_model=SpawnType)
def get_spawn_type(spawn_type_id: str):
    repo = get_repository_factory().get_spawn_type_repository()
    spawn_type = repo.get_by_id(spawn_type_id)
    if not spawn_type:
        raise HTTPException(status_code=404, detail="Spawn type not found")
    return spawn_type


@router.put("/{spawn_type_id}", response_model=SpawnType)
def update_spawn_type(spawn_type_id: str, spawn_type_update: SpawnTypeUpdate):
    repo = get_repository_factory().get_spawn_type_repository()
    existing = repo.get_by_id(spawn_type_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Spawn type not found")
    
    update_data = {}
    if spawn_type_update.name is not None:
        update_data['name'] = spawn_type_update.name
    if spawn_type_update.color is not None:
        update_data['color'] = spawn_type_update.color
    if spawn_type_update.iconType is not None:
        update_data['iconType'] = spawn_type_update.iconType
    if spawn_type_update.rotationEnabled is not None:
        update_data['rotationEnabled'] = spawn_type_update.rotationEnabled
    
    return repo.update(spawn_type_id, update_data)


@router.delete("/{spawn_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spawn_type(spawn_type_id: str):
    repo = get_repository_factory().get_spawn_type_repository()
    existing = repo.get_by_id(spawn_type_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Spawn type not found")
    repo.delete(spawn_type_id)
    return None