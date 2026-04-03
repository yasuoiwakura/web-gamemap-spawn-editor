import json
import os
import sys
import uuid
from datetime import datetime
from decimal import Decimal
from http import HTTPStatus

import boto3
from boto3.dynamodb.conditions import Key

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return int(o) if o % 1 == 0 else float(o)
        return super().default(o)


def _json(obj, status=200, headers=None):
    h = headers or {}
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", **h},
        "body": json.dumps(obj, cls=DecimalEncoder) if obj is not None else "",
    }


def _no_content():
    return {"statusCode": 204, "headers": {}}


def _error(message, status=500):
    return _json({"error": message}, status)


def _now():
    return int(datetime.utcnow().timestamp() * 1000)


def _id():
    return str(uuid.uuid4())


def _body(event):
    raw = event.get("body")
    if raw is None:
        return {}
    return json.loads(raw)


# ---------------------------------------------------------------------------
# DynamoDB tables (lazy, so module import never fails)
# ---------------------------------------------------------------------------

_table_suffix = os.environ.get("TABLE_SUFFIX", "")
_region = os.environ.get("REGION") or os.environ.get("AWS_REGION", "us-east-1")
_ddb = boto3.resource("dynamodb", region_name=_region)

games_tbl = _ddb.Table(f"games{_table_suffix}")
maps_tbl = _ddb.Table(f"maps{_table_suffix}")
spawn_types_tbl = _ddb.Table(f"spawn-types{_table_suffix}")
pois_tbl = _ddb.Table(f"pois{_table_suffix}")
flight_paths_tbl = _ddb.Table(f"flight-paths{_table_suffix}")

ROUTES = []  # populated at startup


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

def get_games():
    return _json(games_tbl.scan().get("Items", []))


def get_game(game_id):
    item = games_tbl.get_item(Key={"id": game_id}).get("Item")
    return _json(item) if item else _error("Game not found", 404)


def post_game(body):
    item = {"id": _id(), "name": body["name"], "createdAt": _now()}
    if body.get("iconUrl"):
        item["iconUrl"] = body["iconUrl"]
    games_tbl.put_item(Item=item)
    return _json(item, 201)


def put_game(game_id, body):
    expr = "SET #n = :name"
    vals = {":name": body["name"]}
    names = {"#n": "name"}
    if body.get("iconUrl") is not None:
        expr += ", iconUrl = :icon"
        vals[":icon"] = body["iconUrl"]
    games_tbl.update_item(Key={"id": game_id}, UpdateExpression=expr,
                          ExpressionAttributeValues=vals, ExpressionAttributeNames=names)
    return _json(games_tbl.get_item(Key={"id": game_id}).get("Item"))


def delete_game(game_id):
    games_tbl.delete_item(Key={"id": game_id})
    return _no_content()


def get_maps(game_id):
    return _json(maps_tbl.query(IndexName="gameId-index",
                                KeyConditionExpression=Key("gameId").eq(game_id)).get("Items", []))


def get_map(map_id):
    item = maps_tbl.get_item(Key={"id": map_id}).get("Item")
    return _json(item) if item else _error("Map not found", 404)


def post_map(game_id, body):
    item = {"id": _id(), "gameId": game_id, "name": body["name"],
            "imageUrl": body["imageUrl"], "widthPx": body["widthPx"],
            "heightPx": body["heightPx"], "createdAt": _now()}
    if body.get("realSizeMeters"):
        item["realSizeMeters"] = body["realSizeMeters"]
    maps_tbl.put_item(Item=item)
    return _json(item, 201)


def put_map(map_id, body):
    updates, vals, names = [], {}, {}
    for field, attr in [("name", "#n"), ("imageUrl", "imageUrl"),
                        ("widthPx", "widthPx"), ("heightPx", "heightPx"),
                        ("realSizeMeters", "realSizeMeters")]:
        if body.get(field) is not None:
            updates.append(f"{attr} = :{field}")
            vals[f":{field}"] = body[field]
            if field == "name":
                names["#n"] = "name"
    if updates:
        maps_tbl.update_item(Key={"id": map_id},
                             UpdateExpression="SET " + ", ".join(updates),
                             ExpressionAttributeValues=vals,
                             ExpressionAttributeNames=names if names else None)
    return _json(maps_tbl.get_item(Key={"id": map_id}).get("Item"))


def delete_map(map_id):
    maps_tbl.delete_item(Key={"id": map_id})
    return _no_content()


def get_spawn_types(game_id):
    return _json(spawn_types_tbl.query(IndexName="gameId-index",
                                       KeyConditionExpression=Key("gameId").eq(game_id)).get("Items", []))


def get_spawn_type(spawn_type_id):
    item = spawn_types_tbl.get_item(Key={"id": spawn_type_id}).get("Item")
    return _json(item) if item else _error("Spawn type not found", 404)


def post_spawn_type(game_id, body):
    item = {"id": _id(), "gameId": game_id, "name": body["name"],
            "color": body["color"], "iconType": body.get("iconType", "dot"),
            "rotationEnabled": body.get("rotationEnabled", False)}
    spawn_types_tbl.put_item(Item=item)
    return _json(item, 201)


def put_spawn_type(spawn_type_id, body):
    updates, vals = [], {}
    for field in ["name", "color", "iconType", "rotationEnabled"]:
        if body.get(field) is not None:
            updates.append(f"{field} = :{field}")
            vals[f":{field}"] = body[field]
    if updates:
        spawn_types_tbl.update_item(Key={"id": spawn_type_id},
                                    UpdateExpression="SET " + ", ".join(updates),
                                    ExpressionAttributeValues=vals)
    return _json(spawn_types_tbl.get_item(Key={"id": spawn_type_id}).get("Item"))


def delete_spawn_type(spawn_type_id):
    spawn_types_tbl.delete_item(Key={"id": spawn_type_id})
    return _no_content()


def get_pois(map_id):
    return _json(pois_tbl.query(IndexName="mapId-index",
                                KeyConditionExpression=Key("mapId").eq(map_id)).get("Items", []))


def get_poi(poi_id):
    item = pois_tbl.get_item(Key={"id": poi_id}).get("Item")
    return _json(item) if item else _error("POI not found", 404)


def post_poi(map_id, body):
    item = {"id": _id(), "mapId": map_id, "spawnTypeId": body["spawnTypeId"],
            "x": body["x"], "y": body["y"], "createdAt": _now()}
    if body.get("rotation") is not None:
        item["rotation"] = body["rotation"]
    if body.get("label"):
        item["label"] = body["label"]
    pois_tbl.put_item(Item=item)
    return _json(item, 201)


def put_poi(poi_id, body):
    updates, vals, names = [], {}, {}
    for field, attr in [("x", "#x"), ("y", "#y"), ("rotation", "rotation"), ("label", "#l")]:
        if body.get(field) is not None:
            updates.append(f"{attr} = :{field}")
            vals[f":{field}"] = body[field]
            if field in ("x", "y", "label"):
                names[attr] = field
    if updates:
        pois_tbl.update_item(Key={"id": poi_id},
                             UpdateExpression="SET " + ", ".join(updates),
                             ExpressionAttributeValues=vals,
                             ExpressionAttributeNames=names)
    return _json(pois_tbl.get_item(Key={"id": poi_id}).get("Item"))


def delete_poi(poi_id):
    pois_tbl.delete_item(Key={"id": poi_id})
    return _no_content()


def get_flight_paths(map_id):
    return _json(flight_paths_tbl.query(IndexName="mapId-index",
                                        KeyConditionExpression=Key("mapId").eq(map_id)).get("Items", []))


def post_flight_path(map_id, body):
    item = {"id": _id(), "mapId": map_id, "startX": body["startX"],
            "startY": body["startY"], "endX": body["endX"],
            "endY": body["endY"], "createdAt": _now()}
    flight_paths_tbl.put_item(Item=item)
    return _json(item, 201)


def delete_flight_path(flight_path_id):
    flight_paths_tbl.delete_item(Key={"id": flight_path_id})
    return _no_content()


# ---------------------------------------------------------------------------
# Router – path → handler
# ---------------------------------------------------------------------------

def _register(method, pattern, handler_fn):
    """Register a route.  pattern may contain {param} placeholders."""
    import re
    regex = "^" + re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", pattern) + "$"
    ROUTES.append((method, re.compile(regex), handler_fn))


# Games
_register("GET", "/games", lambda p, b: get_games())
_register("GET", "/games/{id}", lambda p, b: get_game(p["id"]))
_register("POST", "/games", lambda p, b: post_game(b))
_register("PUT", "/games/{id}", lambda p, b: put_game(p["id"], b))
_register("DELETE", "/games/{id}", lambda p, b: delete_game(p["id"]))

# Maps – nested under game
_register("GET", "/games/{game_id}/maps", lambda p, b: get_maps(p["game_id"]))
_register("POST", "/games/{game_id}/maps", lambda p, b: post_map(p["game_id"], b))
# Maps – direct
_register("GET", "/maps/{id}", lambda p, b: get_map(p["id"]))
_register("PUT", "/maps/{id}", lambda p, b: put_map(p["id"], b))
_register("DELETE", "/maps/{id}", lambda p, b: delete_map(p["id"]))

# Spawn Types – nested under game
_register("GET", "/games/{game_id}/spawn-types", lambda p, b: get_spawn_types(p["game_id"]))
_register("POST", "/games/{game_id}/spawn-types", lambda p, b: post_spawn_type(p["game_id"], b))
# Spawn Types – direct
_register("GET", "/spawn-types/{id}", lambda p, b: get_spawn_type(p["id"]))
_register("PUT", "/spawn-types/{id}", lambda p, b: put_spawn_type(p["id"], b))
_register("DELETE", "/spawn-types/{id}", lambda p, b: delete_spawn_type(p["id"]))

# POIs
_register("GET", "/maps/{map_id}/pois", lambda p, b: get_pois(p["map_id"]))
_register("POST", "/maps/{map_id}/pois", lambda p, b: post_poi(p["map_id"], b))
_register("PUT", "/maps/{map_id}/pois/{id}", lambda p, b: put_poi(p["id"], b))
_register("DELETE", "/maps/{map_id}/pois/{id}", lambda p, b: delete_poi(p["id"]))

# Flight Paths
_register("GET", "/maps/{map_id}/flight-paths", lambda p, b: get_flight_paths(p["map_id"]))
_register("POST", "/maps/{map_id}/flight-paths", lambda p, b: post_flight_path(p["map_id"], b))
_register("DELETE", "/maps/{map_id}/flight-paths/{id}", lambda p, b: delete_flight_path(p["id"]))

# Health
_register("GET", "/health", lambda p, b: _json({"status": "healthy"}))


# ---------------------------------------------------------------------------
# Lambda entry point
# ---------------------------------------------------------------------------

def handler(event, context):
    # HTTP API v2.0: non-$default stage prefixes rawPath with /{stage}
    stage = event.get("requestContext", {}).get("stage", "")
    raw_path = event.get("rawPath", "")
    if stage and raw_path.startswith(f"/{stage}"):
        raw_path = raw_path[len(stage) + 1:] or "/"
        event["rawPath"] = raw_path

    method = event.get("requestContext", {}).get("http", {}).get("method",
                event.get("httpMethod", "")).upper()

    body = _body(event)

    # Log for CloudWatch debugging
    print(f"DEBUG {method} {raw_path}", file=sys.stderr)
    print(f"DEBUG routes registered: {len(ROUTES)}", file=sys.stderr)

    # Match route
    for route_method, regex, handler_fn in ROUTES:
        if route_method == method or route_method == "ANY":
            m = regex.match(raw_path)
            if m:
                try:
                    return handler_fn(m.groupdict(), body)
                except Exception as e:
                    print(f"HANDLER ERROR: {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc()
                    return _error(str(e), 500)

    available = ", ".join(f"{m} {r}" for m, r, _ in ROUTES)
    print(f"DEBUG 404: no route for {method} {raw_path}. Available: {available}", file=sys.stderr)
    return _error("Not Found", 404)
