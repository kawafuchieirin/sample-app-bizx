"""AWS Lambda entry point.

Wraps the FastAPI app with Mangum so API Gateway (HTTP API) events are handled.
The Lambda's handler is configured as `app.lambda_handler.handler`.
"""

from __future__ import annotations

from mangum import Mangum

from app.main import app

handler = Mangum(app)
