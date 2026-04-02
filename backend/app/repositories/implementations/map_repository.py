from typing import Optional, List, Dict, Any
from boto3.dynamodb.conditions import Key
from app.models import Map, MapCreate
from app.repositories.interfaces import MapRepository
from app.repositories.dynamodb_client import DynamoDBClient


class DynamoDBMapRepository(MapRepository):
    def __init__(self, client: DynamoDBClient):
        self._client = client
        self._table = client.table('maps')

    def get_by_game(self, game_id: str) -> List[Map]:
        response = self._table.query(
            KeyConditionExpression=Key('gameId').eq(game_id)
        )
        items = response.get('Items', [])
        return [self._item_to_map(item) for item in items]

    def get_by_id(self, map_id: str) -> Optional[Map]:
        response = self._table.get_item(Key={'id': map_id})
        item = response.get('Item')
        return self._item_to_map(item) if item else None

    def create(self, game_id: str, map_data: MapCreate) -> Map:
        item = {
            'id': self._client.generate_id(),
            'gameId': game_id,
            'name': map_data.name,
            'imageUrl': map_data.imageUrl,
            'widthPx': map_data.widthPx,
            'heightPx': map_data.heightPx,
            'createdAt': self._client.get_timestamp()
        }
        if map_data.realSizeMeters:
            item['realSizeMeters'] = map_data.realSizeMeters
        self._table.put_item(Item=item)
        return self._item_to_map(item)

    def update(self, map_id: str, map_data: dict) -> Optional[Map]:
        update_expr = "SET "
        expr_attr_values = {}
        expr_attr_names = {}
        updates = []

        if map_data.get('name') is not None:
            updates.append("#n = :name")
            expr_attr_names['#n'] = 'name'
            expr_attr_values[':name'] = map_data['name']

        if map_data.get('imageUrl') is not None:
            updates.append("imageUrl = :imageUrl")
            expr_attr_values[':imageUrl'] = map_data['imageUrl']

        if map_data.get('widthPx') is not None:
            updates.append("widthPx = :widthPx")
            expr_attr_values[':widthPx'] = map_data['widthPx']

        if map_data.get('heightPx') is not None:
            updates.append("heightPx = :heightPx")
            expr_attr_values[':heightPx'] = map_data['heightPx']

        if map_data.get('realSizeMeters') is not None:
            updates.append("realSizeMeters = :realSizeMeters")
            expr_attr_values[':realSizeMeters'] = map_data['realSizeMeters']

        if not updates:
            return self.get_by_id(map_id)

        self._table.update_item(
            Key={'id': map_id},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeValues=expr_attr_values,
            ExpressionAttributeNames=expr_attr_names if expr_attr_names else None
        )
        return self.get_by_id(map_id)

    def delete(self, map_id: str) -> bool:
        self._table.delete_item(Key={'id': map_id})
        return True

    def _item_to_map(self, item: Optional[Dict[str, Any]]) -> Optional[Map]:
        if not item:
            return None
        return Map(**item)
