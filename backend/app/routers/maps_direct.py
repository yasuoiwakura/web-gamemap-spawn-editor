from fastapi import APIRouter, HTTPException, status
from typing import Any
from pydantic import BaseModel
from ..services.dynamodb import db_service
from ..utils import cors_response

router = APIRouter(prefix="/maps", tags=["maps"])


class MapUpdate(BaseModel):
    name: str = None
    imageUrl: str = None
    widthPx: int = None
    heightPx: int = None
    realSizeMeters: int = None


@router.get("/{map_id}")
def get_map(map_id: str):
    map_data = db_service.get_map(map_id)
    if not map_data:
        raise HTTPException(status_code=404, detail="Map not found")
    return cors_response(map_data)


@router.put("/{map_id}")
def update_map(map_id: str, map_update: MapUpdate):
    existing = db_service.get_map(map_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Map not found")
    return cors_response(db_service.update_map(
        map_id,
        name=map_update.name,
        image_url=map_update.imageUrl,
        width_px=map_update.widthPx,
        height_px=map_update.heightPx,
        real_size_meters=map_update.realSizeMeters
    ))


@router.delete("/{map_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_map(map_id: str):
    existing = db_service.get_map(map_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Map not found")
    db_service.delete_map(map_id)
    return cors_response(None, status_code=status.HTTP_204_NO_CONTENT)
