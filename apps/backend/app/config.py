"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. All values come from the environment (12-factor)."""

    model_config = SettingsConfigDict(env_prefix="BIZX_", env_file=".env", extra="ignore")

    # DynamoDB
    table_name: str = "bizx-tasks"
    aws_region: str = "ap-northeast-1"
    # Optional endpoint override for local DynamoDB (e.g. http://localhost:8000).
    dynamodb_endpoint_url: str | None = None

    # Cognito (JWT verification)
    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""

    # CORS: comma-separated list of allowed origins.
    cors_origins: str = "http://localhost:5173"

    # When true, JWT signature verification is skipped and the token's `sub`
    # claim is trusted as-is. Intended ONLY for local development / tests.
    auth_disabled: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def cognito_issuer(self) -> str:
        return f"https://cognito-idp.{self.aws_region}.amazonaws.com/{self.cognito_user_pool_id}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
