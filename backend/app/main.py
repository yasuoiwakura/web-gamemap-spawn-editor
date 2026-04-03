from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mangum import Mangum
from .routers import games, maps, maps_direct, spawn_types, spawn_types_direct, pois, flight_paths
import traceback

app = FastAPI(
    title="GameMap Spawn Editor API",
    description="Serverless API for managing game maps, spawn points and flight paths",
    version="1.0.0"
)


@app.exception_handler(Exception)
async def catch_all_exceptions(request: Request, exc: Exception):
    print(f"EXCEPTION: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "traceback": traceback.format_exc()}
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
