from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from ..models import POICreate, POI
from ..services.dynamodb import db_service

router = APIRouter(prefix="/maps/{map_id}/pois", tags=["pois"])


@router.get("", response_model=List[POI])
def get_pois(map_id: str):
    return db_service.get_pois_by_map(map_id)


@router.post("", response_model=POI, status_code=status.HTTP_201_CREATED)
def create_poi(map_id: str, poi: POICreate):
    return db_service.create_poi(
        map_id=map_id,
        spawn_type_id=poi.spawnTypeId,
        x=poi.x,
        y=poi.y,
        rotation=poi.rotation,
        label=poi.label
    )


@router.put("/{poi_id}")
def update_poi(map_id: str, poi_id: str, poi_update: POIUpdate):
    existing = db_service.get_poi(poi_id)
    if not existing or existing.get('mapId') != map_id:
        raise HTTPException(status_code=404, detail="POI not found")
    return db_service.update_poi(
        poi_id,
        x=poi_update.x,
        y=poi_update.y,
        rotation=poi_update.rotation,
        label=poi_update.label
    )


@router.delete("/{poi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poi(map_id: str, poi_id: str):
    existing = db_service.get_poi(poi_id)
    if not existing or existing.get('mapId') != map_id:
        raise HTTPException(status_code=404, detail="POI not found")
    db_service.delete_poi(poi_id)
    return None


class POIUpdate(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    rotation: Optional[float] = None
    label: Optional[str] = None