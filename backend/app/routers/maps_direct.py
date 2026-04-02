from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from ..models import Map
from ..repositories import get_repository_factory

router = APIRouter(prefix="/maps", tags=["maps"])


class MapUpdate(BaseModel):
    name: Optional[str] = None
    imageUrl: Optional[str] = None
    widthPx: Optional[int] = None
    heightPx: Optional[int] = None
    realSizeMeters: Optional[int] = None


@router.get("/{map_id}", response_model=Map)
def get_map(map_id: str):
    repo = get_repository_factory().get_map_repository()
    map_data = repo.get_by_id(map_id)
    if not map_data:
        raise HTTPException(status_code=404, detail="Map not found")
    return map_data


@router.put("/{map_id}", response_model=Map)
def update_map(map_id: str, map_update: MapUpdate):
    repo = get_repository_factory().get_map_repository()
    existing = repo.get_by_id(map_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Map not found")
    
    update_data = {}
    if map_update.name is not None:
        update_data['name'] = map_update.name
    if map_update.imageUrl is not None:
        update_data['imageUrl'] = map_update.imageUrl
    if map_update.widthPx is not None:
        update_data['widthPx'] = map_update.widthPx
    if map_update.heightPx is not None:
        update_data['heightPx'] = map_update.heightPx
    if map_update.realSizeMeters is not None:
        update_data['realSizeMeters'] = map_update.realSizeMeters
    
    return repo.update(map_id, update_data)


@router.delete("/{map_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_map(map_id: str):
    repo = get_repository_factory().get_map_repository()
    existing = repo.get_by_id(map_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Map not found")
    repo.delete(map_id)
    return None