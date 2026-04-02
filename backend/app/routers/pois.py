from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from ..models import POICreate, POI
from ..repositories import get_repository_factory

router = APIRouter(prefix="/maps/{map_id}/pois", tags=["pois"])


@router.get("", response_model=List[POI])
def get_pois(map_id: str):
    repo = get_repository_factory().get_poi_repository()
    return repo.get_by_map(map_id)


@router.post("", response_model=POI, status_code=status.HTTP_201_CREATED)
def create_poi(map_id: str, poi: POICreate):
    repo = get_repository_factory().get_poi_repository()
    return repo.create(map_id, poi)


@router.put("/{poi_id}", response_model=POI)
def update_poi(map_id: str, poi_id: str, poi_update: POIUpdate):
    repo = get_repository_factory().get_poi_repository()
    existing = repo.get_by_id(poi_id)
    if not existing or existing.mapId != map_id:
        raise HTTPException(status_code=404, detail="POI not found")
    
    update_data = {}
    if poi_update.x is not None:
        update_data['x'] = poi_update.x
    if poi_update.y is not None:
        update_data['y'] = poi_update.y
    if poi_update.rotation is not None:
        update_data['rotation'] = poi_update.rotation
    if poi_update.label is not None:
        update_data['label'] = poi_update.label
    
    return repo.update(poi_id, update_data)


@router.delete("/{poi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poi(map_id: str, poi_id: str):
    repo = get_repository_factory().get_poi_repository()
    existing = repo.get_by_id(poi_id)
    if not existing or existing.mapId != map_id:
        raise HTTPException(status_code=404, detail="POI not found")
    repo.delete(poi_id)
    return None


class POIUpdate(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    rotation: Optional[float] = None
    label: Optional[str] = None