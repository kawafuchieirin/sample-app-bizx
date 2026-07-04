"""DynamoDB resource/table access and table creation helpers.

Uses a single table with one GSI:

- Board item: PK=USER#{uid}  SK=BOARD#{bid}
- Task item:  PK=USER#{uid}  SK=TASK#{tid}
              GSI1PK=BOARD#{bid}  GSI1SK=STATUS#{status}#DUE#{due}#{tid}

This lets us:
- List a user's boards:        Query PK=USER#{uid}, begins_with(SK, "BOARD#")
- Get/update/delete a task:    by (PK=USER#{uid}, SK=TASK#{tid}) — O(1), user-scoped
- List a board's tasks:        Query GSI1 PK=BOARD#{bid} (optionally by status), due-sorted
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import boto3

from app.config import get_settings

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

GSI1_NAME = "GSI1"


@lru_cache
def get_dynamodb_resource() -> DynamoDBServiceResource:
    settings = get_settings()
    return boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        endpoint_url=settings.dynamodb_endpoint_url,
    )


def get_table() -> Table:
    return get_dynamodb_resource().Table(get_settings().table_name)


def create_table() -> Table:
    """Create the single table (idempotent-ish; raises if it already exists).

    Used for local development and by moto in tests.
    """
    resource = get_dynamodb_resource()
    table = resource.create_table(
        TableName=get_settings().table_name,
        BillingMode="PAY_PER_REQUEST",
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": GSI1_NAME,
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )
    table.wait_until_exists()
    return table
