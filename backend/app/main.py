from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from mangum import Mangum
from .routers import games, maps, maps_direct, spawn_types, spawn_types_direct, pois, flight_paths

app = FastAPI(
    title="GameMap Spawn Editor API",
    description="Serverless API for managing game maps, spawn points and flight paths",
    version="1.0.0"
)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


class CorsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return Response(
                status_code=204,
                headers=CORS_HEADERS,
                body=""
            )

        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response


app.add_middleware(CorsMiddleware)

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
