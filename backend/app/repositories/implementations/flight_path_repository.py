from typing import Optional, List, Dict, Any
from boto3.dynamodb.conditions import Key
from app.models import FlightPath, FlightPathCreate
from app.repositories.interfaces import FlightPathRepository
from app.repositories.dynamodb_client import DynamoDBClient


class DynamoDBFlightPathRepository(FlightPathRepository):
    def __init__(self, client: DynamoDBClient):
        self._client = client
        self._table = client.table('flight-paths')

    def get_by_map(self, map_id: str) -> List[FlightPath]:
        response = self._table.query(
            KeyConditionExpression=Key('mapId').eq(map_id)
        )
        items = response.get('Items', [])
        return [self._item_to_flight_path(item) for item in items]

    def get_by_id(self, flight_path_id: str) -> Optional[FlightPath]:
        response = self._table.get_item(Key={'id': flight_path_id})
        item = response.get('Item')
        return self._item_to_flight_path(item) if item else None

    def create(self, map_id: str, flight_path: FlightPathCreate) -> FlightPath:
        item = {
            'id': self._client.generate_id(),
            'mapId': map_id,
            'startX': flight_path.startX,
            'startY': flight_path.startY,
            'endX': flight_path.endX,
            'endY': flight_path.endY,
            'createdAt': self._client.get_timestamp()
        }
        self._table.put_item(Item=item)
        return self._item_to_flight_path(item)

    def delete(self, flight_path_id: str) -> bool:
        self._table.delete_item(Key={'id': flight_path_id})
        return True

    def _item_to_flight_path(self, item: Optional[Dict[str, Any]]) -> Optional[FlightPath]:
        if not item:
            return None
        return FlightPath(**item)
