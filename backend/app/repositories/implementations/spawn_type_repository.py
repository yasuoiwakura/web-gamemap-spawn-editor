from typing import Optional, List, Dict, Any
from boto3.dynamodb.conditions import Key
from app.models import SpawnType, SpawnTypeCreate
from app.repositories.interfaces import SpawnTypeRepository
from app.repositories.dynamodb_client import DynamoDBClient


class DynamoDBSpawnTypeRepository(SpawnTypeRepository):
    def __init__(self, client: DynamoDBClient):
        self._client = client
        self._table = client.table('spawn-types')

    def get_by_game(self, game_id: str) -> List[SpawnType]:
        response = self._table.query(
            KeyConditionExpression=Key('gameId').eq(game_id)
        )
        items = response.get('Items', [])
        return [self._item_to_spawn_type(item) for item in items]

    def get_by_id(self, spawn_type_id: str) -> Optional[SpawnType]:
        response = self._table.get_item(Key={'id': spawn_type_id})
        item = response.get('Item')
        return self._item_to_spawn_type(item) if item else None

    def create(self, game_id: str, spawn_type: SpawnTypeCreate) -> SpawnType:
        item = {
            'id': self._client.generate_id(),
            'gameId': game_id,
            'name': spawn_type.name,
            'color': spawn_type.color,
            'iconType': spawn_type.iconType,
            'rotationEnabled': spawn_type.rotationEnabled
        }
        self._table.put_item(Item=item)
        return self._item_to_spawn_type(item)

    def update(self, spawn_type_id: str, spawn_type_data: dict) -> Optional[SpawnType]:
        update_expr = "SET "
        expr_attr_values = {}
        updates = []

        if spawn_type_data.get('name') is not None:
            updates.append("#n = :name")
            expr_attr_values[':name'] = spawn_type_data['name']

        if spawn_type_data.get('color') is not None:
            updates.append("color = :color")
            expr_attr_values[':color'] = spawn_type_data['color']

        if spawn_type_data.get('iconType') is not None:
            updates.append("iconType = :iconType")
            expr_attr_values[':iconType'] = spawn_type_data['iconType']

        if spawn_type_data.get('rotationEnabled') is not None:
            updates.append("rotationEnabled = :rotationEnabled")
            expr_attr_values[':rotationEnabled'] = spawn_type_data['rotationEnabled']

        if not updates:
            return self.get_by_id(spawn_type_id)

        self._table.update_item(
            Key={'id': spawn_type_id},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeValues=expr_attr_values
        )
        return self.get_by_id(spawn_type_id)

    def delete(self, spawn_type_id: str) -> bool:
        self._table.delete_item(Key={'id': spawn_type_id})
        return True

    def _item_to_spawn_type(self, item: Optional[Dict[str, Any]]) -> Optional[SpawnType]:
        if not item:
            return None
        return SpawnType(**item)
