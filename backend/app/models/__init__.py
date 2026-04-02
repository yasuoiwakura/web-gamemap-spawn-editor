from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GameBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    iconUrl: Optional[str] = None


class GameCreate(GameBase):
    pass


class Game(GameBase):
    id: str
    createdAt: int

    class Config:
        from_attributes = True


class MapBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    imageUrl: str
    widthPx: int = Field(..., gt=0)
    heightPx: int = Field(..., gt=0)
    realSizeMeters: Optional[int] = None


class MapCreate(MapBase):
    gameId: str


class Map(MapBase):
    id: str
    gameId: str
    createdAt: int

    class Config:
        from_attributes = True


class SpawnTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    iconType: str = Field(default="dot", pattern=r'^(dot|arrow|custom)$')
    rotationEnabled: bool = False


class SpawnTypeCreate(SpawnTypeBase):
    gameId: str


class SpawnType(SpawnTypeBase):
    id: str
    gameId: str

    class Config:
        from_attributes = True


class POIBase(BaseModel):
    x: float = Field(..., ge=0, le=1000)
    y: float = Field(..., ge=0, le=1000)
    rotation: Optional[float] = Field(None, ge=0, le=360)
    label: Optional[str] = None


class POICreate(POIBase):
    mapId: str
    spawnTypeId: str


class POI(POIBase):
    id: str
    mapId: str
    spawnTypeId: str
    createdAt: int

    class Config:
        from_attributes = True


class FlightPathBase(BaseModel):
    startX: float = Field(..., ge=0, le=1000)
    startY: float = Field(..., ge=0, le=1000)
    endX: float = Field(..., ge=0, le=1000)
    endY: float = Field(..., ge=0, le=1000)


class FlightPathCreate(FlightPathBase):
    mapId: str


class FlightPath(FlightPathBase):
    id: str
    mapId: str
    createdAt: int

    class Config:
        from_attributes = True