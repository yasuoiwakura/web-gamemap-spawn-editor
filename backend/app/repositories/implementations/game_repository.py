from typing import Optional, List, Dict, Any
from app.models import Game, GameCreate
from app.repositories.interfaces import GameRepository
from app.repositories.dynamodb_client import DynamoDBClient


class DynamoDBGameRepository(GameRepository):
    def __init__(self, client: DynamoDBClient):
        self._client = client
        self._table = client.table('games')

    def get_all(self) -> List[Game]:
        response = self._table.scan()
        items = response.get('Items', [])
        return [self._item_to_game(item) for item in items]

    def get_by_id(self, game_id: str) -> Optional[Game]:
        response = self._table.get_item(Key={'id': game_id})
        item = response.get('Item')
        return self._item_to_game(item) if item else None

    def create(self, game: GameCreate) -> Game:
        item = {
            'id': self._client.generate_id(),
            'name': game.name,
            'createdAt': self._client.get_timestamp()
        }
        if game.iconUrl:
            item['iconUrl'] = game.iconUrl
        self._table.put_item(Item=item)
        return self._item_to_game(item)

    def update(self, game_id: str, game: GameCreate) -> Optional[Game]:
        update_expr = "SET #n = :name"
        expr_attr_values = {':name': game.name}
        expr_attr_names = {'#n': 'name'}

        if game.iconUrl is not None:
            update_expr += ", iconUrl = :icon"
            expr_attr_values[':icon'] = game.iconUrl

        self._table.update_item(
            Key={'id': game_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr_values,
            ExpressionAttributeNames=expr_attr_names
        )
        return self.get_by_id(game_id)

    def delete(self, game_id: str) -> bool:
        self._table.delete_item(Key={'id': game_id})
        return True

    def _item_to_game(self, item: Optional[Dict[str, Any]]) -> Optional[Game]:
        if not item:
            return None
        return Game(**item)
