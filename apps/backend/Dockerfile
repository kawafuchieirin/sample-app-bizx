# Lambda container image for the FastAPI backend.
# Build context: apps/backend
FROM public.ecr.aws/lambda/python:3.13

# Install dependencies (no dev group) into the Lambda task root.
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
    uv export --frozen --no-dev --no-emit-project -o requirements.txt && \
    pip install --no-cache-dir -r requirements.txt -t "${LAMBDA_TASK_ROOT}"

# Application code.
COPY app ${LAMBDA_TASK_ROOT}/app

# handler = Mangum(app)
CMD ["app.lambda_handler.handler"]
