import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class DynamoDBService:
    def __init__(self, table_suffix: str = ""):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_suffix = table_suffix
        
        self.games_table = self.dynamodb.Table(f'games{table_suffix}')
        self.maps_table = self.dynamodb.Table(f'maps{table_suffix}')
        self.spawn_types_table = self.dynamodb.Table(f'spawn-types{table_suffix}')
        self.pois_table = self.dynamodb.Table(f'pois{table_suffix}')
        self.flight_paths_table = self.dynamodb.Table(f'flight-paths{table_suffix}')

    def _generate_id(self) -> str:
        return str(uuid.uuid4())

    def _get_timestamp(self) -> int:
        return int(datetime.utcnow().timestamp() * 1000)

    # Games
    def get_all_games(self) -> List[Dict[str, Any]]:
        response = self.games_table.scan()
        return response.get('Items', [])

    def get_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        response = self.games_table.get_item(Key={'id': game_id})
        return response.get('Item')

    def create_game(self, name: str, icon_url: Optional[str] = None) -> Dict[str, Any]:
        item = {
            'id': self._generate_id(),
            'name': name,
            'createdAt': self._get_timestamp()
        }
        if icon_url:
            item['iconUrl'] = icon_url
        self.games_table.put_item(Item=item)
        return item

    def update_game(self, game_id: str, name: str, icon_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        update_expr = "SET #n = :name"
        expr_attr_values = {':name': name}
        expr_attr_names = {'#n': 'name'}
        
        if icon_url is not None:
            update_expr += ", iconUrl = :icon"
            expr_attr_values[':icon'] = icon_url
        
        self.games_table.update_item(
            Key={'id': game_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr_values,
            ExpressionAttributeNames=expr_attr_names
        )
        return self.get_game(game_id)

    def delete_game(self, game_id: str) -> bool:
        self.games_table.delete_item(Key={'id': game_id})
        return True

    # Maps
    def get_maps_by_game(self, game_id: str) -> List[Dict[str, Any]]:
        response = self.maps_table.query(
            KeyConditionExpression=Key('gameId').eq(game_id)
        )
        return response.get('Items', [])

    def get_map(self, map_id: str) -> Optional[Dict[str, Any]]:
        response = self.maps_table.get_item(Key={'id': map_id})
        return response.get('Item')

    def create_map(self, game_id: str, name: str, image_url: str, width_px: int, height_px: int, real_size_meters: Optional[int] = None) -> Dict[str, Any]:
        item = {
            'id': self._generate_id(),
            'gameId': game_id,
            'name': name,
            'imageUrl': image_url,
            'widthPx': width_px,
            'heightPx': height_px,
            'createdAt': self._get_timestamp()
        }
        if real_size_meters:
            item['realSizeMeters'] = real_size_meters
        self.maps_table.put_item(Item=item)
        return item

    def update_map(self, map_id: str, name: str = None, image_url: str = None, width_px: int = None, height_px: int = None, real_size_meters: int = None) -> Optional[Dict[str, Any]]:
        update_expr = "SET "
        expr_attr_values = {}
        expr_attr_names = {}
        updates = []
        
        if name is not None:
            updates.append("#n = :name")
            expr_attr_names['#n'] = 'name'
            expr_attr_values[':name'] = name
        
        if image_url is not None:
            updates.append("imageUrl = :imageUrl")
            expr_attr_values[':imageUrl'] = image_url
        
        if width_px is not None:
            updates.append("widthPx = :widthPx")
            expr_attr_values[':widthPx'] = width_px
        
        if height_px is not None:
            updates.append("heightPx = :heightPx")
            expr_attr_values[':heightPx'] = height_px
        
        if real_size_meters is not None:
            updates.append("realSizeMeters = :realSizeMeters")
            expr_attr_values[':realSizeMeters'] = real_size_meters
        
        if not updates:
            return self.get_map(map_id)
        
        self.maps_table.update_item(
            Key={'id': map_id},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeValues=expr_attr_values,
            ExpressionAttributeNames=expr_attr_names if expr_attr_names else None
        )
        return self.get_map(map_id)

    def delete_map(self, map_id: str) -> bool:
        self.maps_table.delete_item(Key={'id': map_id})
        return True

    # Spawn Types
    def get_spawn_types_by_game(self, game_id: str) -> List[Dict[str, Any]]:
        response = self.spawn_types_table.query(
            KeyConditionExpression=Key('gameId').eq(game_id)
        )
        return response.get('Items', [])

    def get_spawn_type(self, spawn_type_id: str) -> Optional[Dict[str, Any]]:
        response = self.spawn_types_table.get_item(Key={'id': spawn_type_id})
        return response.get('Item')

    def create_spawn_type(self, game_id: str, name: str, color: str, icon_type: str = "dot", rotation_enabled: bool = False) -> Dict[str, Any]:
        item = {
            'id': self._generate_id(),
            'gameId': game_id,
            'name': name,
            'color': color,
            'iconType': icon_type,
            'rotationEnabled': rotation_enabled
        }
        self.spawn_types_table.put_item(Item=item)
        return item

    def update_spawn_type(self, spawn_type_id: str, name: str = None, color: str = None, icon_type: str = None, rotation_enabled: bool = None) -> Optional[Dict[str, Any]]:
        update_expr = "SET "
        expr_attr_values = {}
        updates = []
        
        if name is not None:
            updates.append("#n = :name")
            expr_attr_values[':name'] = name
        
        if color is not None:
            updates.append("color = :color")
            expr_attr_values[':color'] = color
        
        if icon_type is not None:
            updates.append("iconType = :iconType")
            expr_attr_values[':iconType'] = icon_type
        
        if rotation_enabled is not None:
            updates.append("rotationEnabled = :rotationEnabled")
            expr_attr_values[':rotationEnabled'] = rotation_enabled
        
        if not updates:
            return self.get_spawn_type(spawn_type_id)
        
        self.spawn_types_table.update_item(
            Key={'id': spawn_type_id},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeValues=expr_attr_values
        )
        return self.get_spawn_type(spawn_type_id)

    def delete_spawn_type(self, spawn_type_id: str) -> bool:
        self.spawn_types_table.delete_item(Key={'id': spawn_type_id})
        return True

    # POIs
    def get_pois_by_map(self, map_id: str) -> List[Dict[str, Any]]:
        response = self.pois_table.query(
            KeyConditionExpression=Key('mapId').eq(map_id)
        )
        return response.get('Items', [])

    def get_poi(self, poi_id: str) -> Optional[Dict[str, Any]]:
        response = self.pois_table.get_item(Key={'id': poi_id})
        return response.get('Item')

    def create_poi(self, map_id: str, spawn_type_id: str, x: float, y: float, rotation: Optional[float] = None, label: Optional[str] = None) -> Dict[str, Any]:
        item = {
            'id': self._generate_id(),
            'mapId': map_id,
            'spawnTypeId': spawn_type_id,
            'x': x,
            'y': y,
            'createdAt': self._get_timestamp()
        }
        if rotation is not None:
            item['rotation'] = rotation
        if label:
            item['label'] = label
        self.pois_table.put_item(Item=item)
        return item

    def update_poi(self, poi_id: str, x: float = None, y: float = None, rotation: float = None, label: str = None) -> Optional[Dict[str, Any]]:
        update_expr = "SET "
        expr_attr_values = {}
        updates = []
        
        if x is not None:
            updates.append("#x = :x")
            expr_attr_values[':x'] = x
        
        if y is not None:
            updates.append("#y = :y")
            expr_attr_values[':y'] = y
        
        if rotation is not None:
            updates.append("rotation = :rotation")
            expr_attr_values[':rotation'] = rotation
        
        if label is not None:
            updates.append("#l = :label")
            expr_attr_values[':label'] = label
        
        if not updates:
            return self.get_poi(poi_id)
        
        self.pois_table.update_item(
            Key={'id': poi_id},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeValues=expr_attr_values
        )
        return self.get_poi(poi_id)

    def delete_poi(self, poi_id: str) -> bool:
        self.pois_table.delete_item(Key={'id': poi_id})
        return True

    # Flight Paths
    def get_flight_paths_by_map(self, map_id: str) -> List[Dict[str, Any]]:
        response = self.flight_paths_table.query(
            KeyConditionExpression=Key('mapId').eq(map_id)
        )
        return response.get('Items', [])

    def get_flight_path(self, flight_path_id: str) -> Optional[Dict[str, Any]]:
        response = self.flight_paths_table.get_item(Key={'id': flight_path_id})
        return response.get('Item')

    def create_flight_path(self, map_id: str, start_x: float, start_y: float, end_x: float, end_y: float) -> Dict[str, Any]:
        item = {
            'id': self._generate_id(),
            'mapId': map_id,
            'startX': start_x,
            'startY': start_y,
            'endX': end_x,
            'endY': end_y,
            'createdAt': self._get_timestamp()
        }
        self.flight_paths_table.put_item(Item=item)
        return item

    def delete_flight_path(self, flight_path_id: str) -> bool:
        self.flight_paths_table.delete_item(Key={'id': flight_path_id})
        return True


# Singleton instance
db_service = DynamoDBService(table_suffix=os.environ.get('TABLE_SUFFIX', ''))