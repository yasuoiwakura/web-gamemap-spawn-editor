from decimal import Decimal
from fastapi.responses import JSONResponse
from typing import Any

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def _convert_decimals(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimals(item) for item in obj]
    return obj


def cors_response(content: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        content=_convert_decimals(content),
        status_code=status_code,
        headers=CORS_HEADERS
    )
