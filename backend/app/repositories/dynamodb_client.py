import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class DynamoDBClient:
    def __init__(self, table_suffix: str = ""):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_suffix = table_suffix

    def table(self, table_name: str):
        return self.dynamodb.Table(f'{table_name}{self.table_suffix}')

    def generate_id(self) -> str:
        return str(uuid.uuid4())

    def get_timestamp(self) -> int:
        return int(datetime.utcnow().timestamp() * 1000)
