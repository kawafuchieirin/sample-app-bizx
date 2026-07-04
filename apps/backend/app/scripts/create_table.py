"""Create the DynamoDB table for local development.

Usage (with a local DynamoDB running, e.g. via docker):
    BIZX_DYNAMODB_ENDPOINT_URL=http://localhost:8000 \
    BIZX_AWS_REGION=ap-northeast-1 \
    python -m app.scripts.create_table
"""

from __future__ import annotations

from botocore.exceptions import ClientError

from app.config import get_settings
from app.db.table import create_table


def main() -> None:
    settings = get_settings()
    try:
        create_table()
        print(f"created table: {settings.table_name}")
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code == "ResourceInUseException":
            print(f"table already exists: {settings.table_name}")
        else:
            raise


if __name__ == "__main__":
    main()
