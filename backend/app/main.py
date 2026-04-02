from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from .routers import games, maps, maps_direct, spawn_types, spawn_types_direct, pois, flight_paths

app = FastAPI(
    title="GameMap Spawn Editor API",
    description="Serverless API for managing game maps, spawn points and flight paths",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(maps.router)
app.include_router(maps_direct.router)
app.include_router(spawn_types.router)
app.include_router(spawn_types_direct.router)
app.include_router(pois.router)
app.include_router(flight_paths.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


handler = Mangum(app)