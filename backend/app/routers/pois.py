from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from ..models import POICreate, POI
from ..services.dynamodb import db_service
from ..utils import cors_response

router = APIRouter(prefix="/maps/{map_id}/pois", tags=["pois"])


@router.get("")
def get_pois(map_id: str):
    return cors_response(db_service.get_pois_by_map(map_id))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_poi(map_id: str, poi: POICreate):
    return cors_response(
        db_service.create_poi(
            map_id=map_id,
            spawn_type_id=poi.spawnTypeId,
            x=poi.x,
            y=poi.y,
            rotation=poi.rotation,
            label=poi.label
        ),
        status_code=status.HTTP_201_CREATED
    )


@router.put("/{poi_id}")
def update_poi(map_id: str, poi_id: str, poi_update: POIUpdate):
    existing = db_service.get_poi(poi_id)
    if not existing or existing.get('mapId') != map_id:
        raise HTTPException(status_code=404, detail="POI not found")
    return cors_response(db_service.update_poi(
        poi_id,
        x=poi_update.x,
        y=poi_update.y,
        rotation=poi_update.rotation,
        label=poi_update.label
    ))


@router.delete("/{poi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poi(map_id: str, poi_id: str):
    existing = db_service.get_poi(poi_id)
    if not existing or existing.get('mapId') != map_id:
        raise HTTPException(status_code=404, detail="POI not found")
    db_service.delete_poi(poi_id)
    return cors_response(None, status_code=status.HTTP_204_NO_CONTENT)


class POIUpdate(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    rotation: Optional[float] = None
    label: Optional[str] = None
