"""Cognito JWT verification.

In production, access tokens issued by the configured Cognito User Pool are
verified against the pool's JWKS. For local development and tests, set
BIZX_AUTH_DISABLED=true to trust the token's `sub` claim without verifying the
signature (never enable this in a deployed environment).
"""

from __future__ import annotations

from functools import lru_cache

import jwt
from jwt import PyJWKClient

from app.config import Settings


class AuthError(Exception):
    """Raised when a token is missing required claims or fails verification."""


@lru_cache
def _jwks_client(jwks_uri: str) -> PyJWKClient:
    return PyJWKClient(jwks_uri)


def verify_token(token: str, settings: Settings) -> str:
    """Verify a bearer token and return the authenticated user id (`sub`)."""
    if settings.auth_disabled:
        claims = jwt.decode(token, options={"verify_signature": False})
        sub = claims.get("sub")
        if not sub:
            raise AuthError("token has no 'sub' claim")
        return str(sub)

    if not settings.cognito_user_pool_id or not settings.cognito_client_id:
        raise AuthError("Cognito is not configured")

    jwks_uri = f"{settings.cognito_issuer}/.well-known/jwks.json"
    try:
        signing_key = _jwks_client(jwks_uri).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.cognito_issuer,
            options={"require": ["exp", "sub", "iss"]},
        )
    except jwt.PyJWTError as exc:  # noqa: F841 - re-raised with a clean message
        raise AuthError("invalid token") from exc

    # Cognito access tokens carry the app client id in `client_id`; id tokens
    # use `aud`. Accept either so both token types work.
    token_client = claims.get("client_id") or claims.get("aud")
    if token_client != settings.cognito_client_id:
        raise AuthError("token was not issued for this application")

    sub = claims.get("sub")
    if not sub:
        raise AuthError("token has no 'sub' claim")
    return str(sub)
