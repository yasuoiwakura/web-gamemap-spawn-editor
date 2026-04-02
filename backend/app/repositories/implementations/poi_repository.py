from typing import Optional, List, Dict, Any
from boto3.dynamodb.conditions import Key
from app.models import POI, POICreate
from app.repositories.interfaces import POIRepository
from app.repositories.dynamodb_client import DynamoDBClient


class DynamoDBPOIRepository(POIRepository):
    def __init__(self, client: DynamoDBClient):
        self._client = client
        self._table = client.table('pois')

    def get_by_map(self, map_id: str) -> List[POI]:
        response = self._table.query(
            KeyConditionExpression=Key('mapId').eq(map_id)
        )
        items = response.get('Items', [])
        return [self._item_to_poi(item) for item in items]

    def get_by_id(self, poi_id: str) -> Optional[POI]:
        response = self._table.get_item(Key={'id': poi_id})
        item = response.get('Item')
        return self._item_to_poi(item) if item else None

    def create(self, map_id: str, poi: POICreate) -> POI:
        item = {
            'id': self._client.generate_id(),
            'mapId': map_id,
            'spawnTypeId': poi.spawnTypeId,
            'x': poi.x,
            'y': poi.y,
            'createdAt': self._client.get_timestamp()
        }
        if poi.rotation is not None:
            item['rotation'] = poi.rotation
        if poi.label:
            item['label'] = poi.label
        self._table.put_item(Item=item)
        return self._item_to_poi(item)

    def update(self, poi_id: str, poi_data: dict) -> Optional[POI]:
        update_expr = "SET "
        expr_attr_values = {}
        updates = []

        if poi_data.get('x') is not None:
            updates.append("#x = :x")
            expr_attr_values[':x'] = poi_data['x']

        if poi_data.get('y') is not None:
            updates.append("#y = :y")
            expr_attr_values[':y'] = poi_data['y']

        if poi_data.get('rotation') is not None:
            updates.append("rotation = :rotation")
            expr_attr_values[':rotation'] = poi_data['rotation']

        if poi_data.get('label') is not None:
            updates.append("#l = :label")
            expr_attr_values[':label'] = poi_data['label']

        if not updates:
            return self.get_by_id(poi_id)

        self._table.update_item(
            Key={'id': poi_id},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeValues=expr_attr_values
        )
        return self.get_by_id(poi_id)

    def delete(self, poi_id: str) -> bool:
        self._table.delete_item(Key={'id': poi_id})
        return True

    def _item_to_poi(self, item: Optional[Dict[str, Any]]) -> Optional[POI]:
        if not item:
            return None
        return POI(**item)
