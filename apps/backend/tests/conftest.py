"""Shared test fixtures: moto-mocked DynamoDB and an authenticated client."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator

# Configure the app for tests BEFORE importing any app module.
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")
os.environ["BIZX_AWS_REGION"] = "ap-northeast-1"
os.environ["BIZX_TABLE_NAME"] = "bizx-tasks-test"
os.environ["BIZX_AUTH_DISABLED"] = "true"

import jwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from moto import mock_aws  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db import table as table_mod  # noqa: E402


@pytest.fixture(autouse=True)
def _dynamo() -> Iterator[None]:
    """Provide a fresh moto-backed table for every test."""
    get_settings.cache_clear()
    with mock_aws():
        table_mod.get_dynamodb_resource.cache_clear()
        table_mod.create_table()
        yield
        table_mod.get_dynamodb_resource.cache_clear()


@pytest.fixture
def client() -> TestClient:
    from app.main import create_app

    return TestClient(create_app())


@pytest.fixture
def auth_headers() -> Callable[..., dict[str, str]]:
    def _make(user_id: str = "user-1") -> dict[str, str]:
        token = jwt.encode(
            {"sub": user_id}, "test-signing-key-at-least-32-bytes!", algorithm="HS256"
        )
        return {"Authorization": f"Bearer {token}"}

    return _make
